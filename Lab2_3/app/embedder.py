"""Embedding worker."""
from celery import Celery
from docker_logs import get_logger
from mongodb_worker import save_submission

import fasttext
from nltk.tokenize import WordPunctTokenizer
import numpy as np

logging = get_logger("embedder")
app = Celery('celery_base', broker='amqp://localhost//', backend='amqp')

tokenizer = WordPunctTokenizer()
model_name = 'dbpedia.bin'
ft_model = fasttext.load_model(model_name)


@app.task(bind=True)
def embedding(self, work, submissions):
    """Embedds given submissions texts."""
    total = sum([len(s["comments"]) for s in submissions])
    logging.info(f'{work}: Submissions {len(submissions)} embedded'
                 f' with total {total} comments')
    for submission in submissions:
        subm_vectors = [ft_model[token] for token in
                        tokenizer.tokenize(submission['text'])]
        for comment in submission['comments']:
            subm_vectors.extend([ft_model[token] for token in
                                 tokenizer.tokenize(comment)])
        if len(subm_vectors) > 0:
            vector = np.mean(subm_vectors, axis=0).tolist()
            submission['text_embedded'] = vector
            save_submission.apply_async(args=['mongodb_worker', submission],
                                        queue='mongodb_tasks')
