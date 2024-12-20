from flask import Flask, request, send_file, render_template, jsonify
from flask_compress import Compress
from PIL import Image
import io
import zipfile
from werkzeug.utils import secure_filename
import imghdr
import os

app = Flask(__name__,
    static_url_path='/static',
    static_folder='static')
Compress(app)

# Расширенный список поддерживаемых форматов
ALLOWED_FORMATS = [
    'PNG', 'JPEG', 'JPG', 'WEBP', 'BMP', 'ICO', 'TIFF', 'GIF',
    'EPS', 'PCX', 'PPM', 'SGI', 'SPIDER', 'TGA', 'XBM'
]

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@app.route('/')
def index():
    return render_template('index.html', formats=ALLOWED_FORMATS)


@app.route('/convert', methods=['POST'])
def convert():
    try:
        target_format = request.form['format'].lower()
        quality = int(request.form.get('quality', 90))

        if target_format.upper() not in ALLOWED_FORMATS:
            return jsonify({'error': 'Unsupported format'}), 400

        files = request.files.getlist('files')

        if not files:
            return jsonify({'error': 'No files selected'}), 400

        # Создаем объект байтов для хранения ZIP-архива в памяти
        memory_zip = io.BytesIO()

        with zipfile.ZipFile(memory_zip, 'w') as zipf:
            errors = []

            for file in files:
                if file.filename:
                    # Читаем файл в память
                    file_content = file.read()

                    if len(file_content) > MAX_FILE_SIZE:
                        errors.append(f"{file.filename} exceeds maximum size limit")
                        continue

                    filename = secure_filename(file.filename)
                    base_name = os.path.splitext(filename)[0]

                    try:
                        # Создаем объект изображения из байтов
                        image = Image.open(io.BytesIO(file_content))

                        if image.mode == 'RGBA' and target_format.upper() in ['JPEG', 'JPG']:
                            image = image.convert('RGB')

                        # Создаем буфер для сконвертированного изображения
                        output_buffer = io.BytesIO()

                        save_kwargs = {}
                        if target_format.upper() in ['JPEG', 'JPG', 'WEBP']:
                            save_kwargs['quality'] = quality

                        # Сохраняем сконвертированное изображение в буфер
                        image.save(output_buffer, format=target_format.upper(), **save_kwargs)

                        # Добавляем файл в ZIP-архив
                        zipf.writestr(
                            f"{base_name}.{target_format}",
                            output_buffer.getvalue()
                        )

                    except Exception as e:
                        errors.append(f"Error converting {filename}: {str(e)}")
                        continue

            if zipf.filelist:
                # Перемещаем указатель в начало буфера
                memory_zip.seek(0)

                return send_file(
                    memory_zip,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name='converted_images.zip'
                )
            else:
                return jsonify({
                    'error': 'No files were converted successfully',
                    'details': errors
                }), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=24008)