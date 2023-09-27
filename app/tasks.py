import time
from rq import get_current_job
from app import create_app, db
from app.models import Task, User, Post
import sys

app = create_app()
app.app_context().push()


def example(seconds):
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')

# Example of using Redis with tasks
def export_posts(user_id):
    try:
       user = User.query.get(user_id)
       _set_task_progress(0)
       data = []
       i = 0
       total_posts = user.posts.count()
       for post in user.posts.order_by(Post.timestamp.asc()):
           data.append({'body': post.body,
                        'timestamp': post.timestamp.isoformat() + 'Z'})
           time.sleep(5)
           i += 1
           _set_task_progress(100 * i // total_posts)
    except:
        pass
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(),
                                                     'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()
