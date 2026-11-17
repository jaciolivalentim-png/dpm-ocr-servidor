"""Servidor OCR isolado para DPM Inteligente 4.1 (somente imagens PNG)."""
import hmac
import io
import logging
import os
import subprocess
import sys
import tempfile
from flask import Flask, Response, request
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 8_000_000

@app.get('/health')
def health():
    return Response('ok', mimetype='text/plain')

@app.post('/ocr')
def ocr():
    secret = os.environ.get('DPM_OCR_REMOTE_TOKEN', '')
    supplied = request.headers.get('Authorization', '')
    if not secret or not hmac.compare_digest(supplied, 'Bearer ' + secret):
        return Response('Não autorizado', status=401)
    if request.mimetype != 'image/png':
        return Response('Formato inválido: envie image/png', status=415)
    try:
        data = request.get_data(cache=False)
        with Image.open(io.BytesIO(data)) as img:
            if img.format != 'PNG' or img.width * img.height > 8_000_000:
                return Response('Imagem inválida', status=400)
            with tempfile.TemporaryDirectory() as directory:
                path = os.path.join(directory, 'input.png')
                img.convert('RGB').save(path, format='PNG')
                env = os.environ.copy()
                for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
                    env[name] = '1'
                try:
                    result = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr_worker.py'), path],
                        capture_output=True, text=True, timeout=150, env=env, check=False)
                except subprocess.TimeoutExpired:
                    return Response('Tempo de OCR excedido', status=504)
                if result.returncode:
                    app.logger.error('OCR subprocess failed code=%s; stderr_tail=%r', result.returncode, (result.stderr or '')[-1800:])
                    return Response('Falha ao processar imagem; consulte logs do servidor OCR', status=422)
                recognized = result.stdout.strip()
                app.logger.info('OCR_RESULT characters=%s image_pixels=%s', len(recognized), img.width * img.height)
                if not recognized:
                    return Response('OCR executado, mas nenhum texto foi reconhecido', status=422)
                return Response(recognized[:2_000_000], mimetype='text/plain; charset=utf-8')
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        return Response('Imagem inválida ou não processável', status=422)

@app.errorhandler(413)
def too_large(error):
    return Response('Arquivo acima de 12 MB', status=413)
