import os
import glob
from PIL import Image
from pillow_heif import register_heif_opener
import img2pdf
from pathlib import Path
from datetime import datetime

# 注册HEIF/HEIC支持
register_heif_opener()

def convert_images_to_pdf():
    # 设置路径
    images_dir = "images"
    
    # 生成输出文件名：文件夹名_日期.pdf
    folder_name = os.path.basename(os.path.abspath(images_dir))
    current_date = datetime.now().strftime("%Y%m%d")
    output_pdf = f"{folder_name}_{current_date}.pdf"
    
    # 支持的图片格式
    supported_formats = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', '*.heic', '*.webp', '*.gif']
    
    # 获取所有支持的图片文件并按文件名排序
    image_files = []
    for format_pattern in supported_formats:
        files = glob.glob(os.path.join(images_dir, format_pattern))
        files.extend(glob.glob(os.path.join(images_dir, format_pattern.upper())))
        image_files.extend(files)
    
    # 去重并排序
    image_files = list(set(image_files))
    image_files.sort()
    
    if not image_files:
        print("未找到支持的图片文件")
        print(f"支持的格式: {', '.join([fmt.replace('*.', '') for fmt in supported_formats])}")
        return
    
    print(f"找到 {len(image_files)} 个图片文件")
    print(f"输出文件: {output_pdf}")
    
    # 临时存储转换后的图片
    converted_images = []
    temp_dir = "temp_converted"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # 处理所有图片文件
        for i, image_file in enumerate(image_files):
            print(f"正在处理: {os.path.basename(image_file)} ({i+1}/{len(image_files)})")
            
            try:
                # 打开图片
                with Image.open(image_file) as img:
                    # 转换为RGB模式（如果需要）
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # 对于透明图片，创建白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 保存为临时JPEG文件
                    temp_filename = os.path.join(temp_dir, f"temp_{i:04d}.jpg")
                    img.save(temp_filename, "JPEG", quality=95)
                    converted_images.append(temp_filename)
                    
            except Exception as e:
                print(f"处理文件 {os.path.basename(image_file)} 时出错: {e}")
                continue
        
        if not converted_images:
            print("没有成功处理的图片文件")
            return
        
        # 将所有图片合并为PDF
        print("正在创建PDF文件...")
        with open(output_pdf, "wb") as f:
            f.write(img2pdf.convert(converted_images))
        
        print(f"PDF文件已创建: {output_pdf}")
        print(f"成功处理了 {len(converted_images)} 个图片文件")
        
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
    
    finally:
        # 清理临时文件
        print("清理临时文件...")
        for temp_file in converted_images:
            try:
                os.remove(temp_file)
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

if __name__ == "__main__":
    convert_images_to_pdf()