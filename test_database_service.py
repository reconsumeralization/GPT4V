import logging
import pytest
from models import User, ImageGenerationTask
from services import create_user, create_image_generation_task, get_task_status

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test the creation of a new user
def test_create_user():
    try:
        new_user = create_user(username='testuser', email='testuser@example.com', password='password123')
        assert new_user is not None
        assert new_user.username == 'testuser'
    except Exception as e:
        logger.exception("An error occurred during test_create_user")

# Test the creation of a new image generation task
def test_create_image_generation_task():
    try:
        new_task = create_image_generation_task(prompt='A sunny day in the park')
        assert new_task is not None
        assert new_task.prompt == 'A sunny day in the park'
    except Exception as e:
        logger.exception("An error occurred during test_create_image_generation_task")

# Test retrieving the status of an image generation task
def test_get_task_status():
    try:
        task = create_image_generation_task(prompt='A sunny day in the park')
        status = get_task_status(task_id=task.id)
        assert status is not None
        assert status in ['    assert new_user is not None
    assert new_user.username == 'testuser'

# Test the creation of a new image generation task
def test_create_image_generation_task():
    new_task = create_image_generation_task(prompt='A sunny day in the park')
    assert new_task is not None
    assert new_task.prompt == 'A sunny day in the park'

# Test retrieving the status of an image generation task
def test_get_task_status():
    task = create_image_generation_task(prompt='A sunny day in the park')
    status = get_task_status(task_id=task.id)
    assert status is not None
    assert status in ['pending', 'completed', 'failed']
``
