# web_app.py

import os
import time
from pathlib import Path
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid

from video_processor import VideoProcessor

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload size
    app.config['UPLOAD_FOLDER'] = str(Path(__file__).parent / "uploads")
    app.config['RESULTS_FOLDER'] = str(Path(__file__).parent / "results")
    
    # 确保上传和结果目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    
    # 初始化视频处理器
    processor = VideoProcessor()
    
    @app.route('/')
    def home():
        return render_template('index.html')
    
    @app.route('/process', methods=['POST'])
    def process_video():
        """处理用户提交的视频（URL或文件）"""
        process_type = request.form.get('type')
        job_id = str(uuid.uuid4())
        result_dir = Path(app.config['RESULTS_FOLDER']) / job_id
        result_dir.mkdir(exist_ok=True)
        
        try:
            if process_type == 'url':
                # 处理单个URL
                url = request.form.get('url')
                if not url:
                    return jsonify({'error': '未提供URL'}), 400
                
                output_file = result_dir / 'result.txt'
                text = processor.process_video_url(url, str(output_file))
                
                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'text': text,
                    'download_url': f'/download/{job_id}/result.txt'
                })
                
            elif process_type == 'file':
                # 处理上传的视频文件
                if 'video' not in request.files:
                    return jsonify({'error': '未上传视频文件'}), 400
                
                video_file = request.files['video']
                if video_file.filename == '':
                    return jsonify({'error': '未选择文件'}), 400
                
                filename = secure_filename(video_file.filename)
                file_path = Path(app.config['UPLOAD_FOLDER']) / f"{job_id}_{filename}"
                video_file.save(str(file_path))
                
                output_file = result_dir / 'result.txt'
                text = processor.process_local_video(file_path, str(output_file))
                
                # 处理完成后删除上传的视频文件
                if file_path.exists():
                    file_path.unlink()
                
                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'text': text,
                    'download_url': f'/download/{job_id}/result.txt'
                })
                
            elif process_type == 'multiple_urls':
                # 处理多个URL
                urls_text = request.form.get('urls')
                if not urls_text:
                    return jsonify({'error': '未提供URL列表'}), 400
                
                urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
                results = processor.process_multiple_urls(urls, result_dir)
                
                # 创建一个合并的结果文件
                merged_file = result_dir / 'all_results.txt'
                with open(merged_file, 'w', encoding='utf-8') as f:
                    for url, text in results.items():
                        f.write(f"=== {url} ===\n\n")
                        f.write(text)
                        f.write("\n\n" + "="*80 + "\n\n")
                
                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'results': results,
                    'download_url': f'/download/{job_id}/all_results.txt'
                })
                
            elif process_type == 'url_file':
                # 处理包含URL的文本文件
                if 'url_file' not in request.files:
                    return jsonify({'error': '未上传URL文件'}), 400
                
                url_file = request.files['url_file']
                if url_file.filename == '':
                    return jsonify({'error': '未选择文件'}), 400
                
                filename = secure_filename(url_file.filename)
                file_path = Path(app.config['UPLOAD_FOLDER']) / f"{job_id}_{filename}"
                url_file.save(str(file_path))
                
                results = processor.process_url_file(file_path, result_dir)
                
                # 处理完成后删除上传的URL文件
                if file_path.exists():
                    file_path.unlink()
                
                # 创建一个合并的结果文件
                merged_file = result_dir / 'all_results.txt'
                with open(merged_file, 'w', encoding='utf-8') as f:
                    for url, text in results.items():
                        f.write(f"=== {url} ===\n\n")
                        f.write(text)
                        f.write("\n\n" + "="*80 + "\n\n")
                
                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'results': results,
                    'download_url': f'/download/{job_id}/all_results.txt'
                })
            
            else:
                return jsonify({'error': '不支持的处理类型'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/download/<job_id>/<filename>')
    def download_file(job_id, filename):
        """下载转录结果文件"""
        result_dir = os.path.join(app.config['RESULTS_FOLDER'], job_id)
        return send_from_directory(result_dir, filename, as_attachment=True)
    
    return app
