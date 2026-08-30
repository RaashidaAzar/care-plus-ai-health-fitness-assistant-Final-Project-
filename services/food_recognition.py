import os
import json
import tempfile
import traceback
import zipfile
from shutil import copyfileobj
from pathlib import Path

import numpy as np
from PIL import Image

from config import Config
from database.models import Nutrition
from services.food_labels import EXPECTED_CLASS_COUNT, FOOD_LABELS, food_key

_FOOD_MODEL = None
_FOOD_MODEL_ERROR = None


def _load_legacy_keras_model(keras, model_path):
    from keras.src.models.functional import Functional

    with zipfile.ZipFile(model_path) as archive:
        config = json.loads(archive.read('config.json'))
        weights_name = 'model.weights.h5'

        def fix_config(node):
            if isinstance(node, dict):
                if node.get('class_name') == 'BatchNormalization':
                    axis = node.get('config', {}).get('axis')
                    if isinstance(axis, list) and axis:
                        node['config']['axis'] = axis[0]
                elif node.get('class_name') == 'DepthwiseConv2D':
                    node.get('config', {}).pop('groups', None)
                for value in node.values():
                    fix_config(value)
            elif isinstance(node, list):
                for value in node:
                    fix_config(value)

        fix_config(config)
        config['compile_config'] = None
        model = keras.models.model_from_json(
            json.dumps(config), custom_objects={'Functional': Functional}
        )
        temporary_fd, temporary_path = tempfile.mkstemp(suffix='.weights.h5')
        os.close(temporary_fd)
        with open(temporary_path, 'wb') as target:
            with archive.open(weights_name) as source:
                copyfileobj(source, target)
    model.load_weights(temporary_path)
    Path(temporary_path).unlink(missing_ok=True)
    return model


def _get_food_model():
    global _FOOD_MODEL, _FOOD_MODEL_ERROR
    if _FOOD_MODEL is not None:
        return _FOOD_MODEL

    model_path = Config.MODEL_FOOD_PATH
    if not model_path.exists():
        _FOOD_MODEL_ERROR = f'Model file not found at {model_path}'
        return None

    try:
        import keras

        try:
            _FOOD_MODEL = keras.models.load_model(str(model_path), compile=False)
        except (TypeError, ValueError):
            _FOOD_MODEL = _load_legacy_keras_model(keras, model_path)
        input_shape = tuple(_FOOD_MODEL.input_shape)
        output_shape = tuple(_FOOD_MODEL.output_shape)
        if input_shape != (None, 224, 224, 3):
            raise ValueError(f'Unexpected food model input shape: {input_shape}')
        if output_shape != (None, EXPECTED_CLASS_COUNT):
            raise ValueError(f'Unexpected food model output shape: {output_shape}')
        print(f'Model loaded successfully: {model_path}', flush=True)
        print(f'Model input shape: {input_shape}', flush=True)
        print(f'Model output classes: {output_shape[-1]}', flush=True)
        return _FOOD_MODEL
    except Exception as error:
        _FOOD_MODEL_ERROR = f'{type(error).__name__}: {error}'
        print(f'Error loading food model from {model_path}: {_FOOD_MODEL_ERROR}', flush=True)
        return None


def food_model_status():
    model = _get_food_model()
    return {
        'available': model is not None,
        'path': str(Config.MODEL_FOOD_PATH),
        'error': _FOOD_MODEL_ERROR,
        'input_shape': list(model.input_shape) if model is not None else None,
        'output_shape': list(model.output_shape) if model is not None else None,
        'class_count': EXPECTED_CLASS_COUNT,
    }


def _nutrition_for(food_name):
    nutrition_entry = Nutrition.query.filter_by(food_name=food_key(food_name)).first()
    return nutrition_entry, {
        'calories': float(nutrition_entry.calories) if nutrition_entry else 150.0,
        'protein': float(nutrition_entry.protein) if nutrition_entry else 5.0,
        'carbohydrates': float(nutrition_entry.carbohydrates) if nutrition_entry else 20.0,
        'fat': float(nutrition_entry.fat) if nutrition_entry else 5.0,
        'fibre': float(nutrition_entry.fibre) if nutrition_entry else 2.0,
        'sugar': float(nutrition_entry.sugar) if nutrition_entry else 2.0,
    }


def predict_food_image(file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        return {'error': 'Unable to process this image. File does not exist.'}

    try:
        with Image.open(file_path) as image:
            image_array = np.asarray(image.convert('RGB').resize((224, 224)), dtype=np.float32)
            image_batch = np.expand_dims(image_array, axis=0)
    except Exception:
        return {'error': 'Unable to process this image. Please upload a valid JPG, PNG, or WEBP food image.'}

    model = _get_food_model()
    if model is None:
        return {'error': f'AI food recognition model could not be loaded. {_FOOD_MODEL_ERROR}'}

    try:
        predictions = np.asarray(model.predict(image_batch, verbose=0))[0]
        class_index = int(np.argmax(predictions))
        if not 0 <= class_index < EXPECTED_CLASS_COUNT:
            raise ValueError(f'Model returned invalid class index: {class_index}')

        label = FOOD_LABELS[class_index]
        confidence = float(predictions[class_index])
        top_indices = np.argsort(predictions)[-5:][::-1]
        top_predictions = [
            {'class': FOOD_LABELS[int(index)], 'confidence': float(predictions[index])}
            for index in top_indices
        ]
        nutrition_entry, nutrition = _nutrition_for(label)
        calories = nutrition['calories']
        if calories <= 150:
            health_suggestion = 'Good'
        elif calories <= 300:
            health_suggestion = 'Moderate'
        else:
            health_suggestion = 'Avoid frequently'
        return {
            'error': None,
            'success': True,
            'prediction': label,
            'food_name': label,
            'raw_food_name': food_key(label),
            'confidence': confidence,
            'confidence_percent': round(confidence * 100, 1),
            'class_index': class_index,
            'top_predictions': top_predictions,
            'serving_size_g': float(nutrition_entry.serving_size_g) if nutrition_entry else 100.0,
            'nutrition': nutrition,
            'health_suggestion': health_suggestion,
        }
    except Exception as error:
        traceback.print_exc()
        return {'error': f'Prediction failed: {type(error).__name__}: {error}'}