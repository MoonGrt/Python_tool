#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 将文件夹下的图片居中剪裁为指定比例并缩放到指定大小

from PIL import Image, UnidentifiedImageError
from pathlib import Path
import sys
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np

# 目标尺寸
dst_w = 512
dst_h = 512

# 全局变量，指定缩放算法，默认为LANCZOS
resize_algorithm = Image.Resampling.LANCZOS
metrics_list = []

# 缩放算法映射字典
resampling_options = {
    "1": Image.Resampling.NEAREST,
    "2": Image.Resampling.BILINEAR,
    "3": Image.Resampling.BICUBIC,
    "4": Image.Resampling.HAMMING,
    "5": Image.Resampling.BOX,
    "6": Image.Resampling.LANCZOS,
}

# def calculate_metrics(original, generated):
#     # 计算 SSIM
#     ssim_value, _ = ssim(original, generated, full=True)
#     # 计算 MSE
#     mse = np.sum((original - generated) ** 2) / float(original.size)
#     # 计算 PSNR
#     psnr = cv2.PSNR(original, generated)
#     return ssim_value, mse, psnr

def remove_ds_store(path):
    # print('检查 %s 内是否存在 .DS_Store 文件'%str(path))
    target = path/'.DS_Store'
    if (target.exists()):
        Path.unlink(target)
        print(f'{target} 文件已自动删除。')
    else:
        # print(f'.DS_Store 文件不存在，继续操作。')
        pass
    
def resize_dir_images(src_path):
    global filecount, metrics_list
    remove_ds_store(src_path)  
    for f in src_path.glob('**/*'):  # 也可以用src_path.rglob('*')
        if f.is_file():
            filecount += 1
            print('正在转换第 %d 个文件:%s       \r'%(filecount,f.name),end='')
            crop_and_resize(f)
            # metrics_list.append(crop_and_resize(f))

def crop_and_resize(fp):
    ''' 图片按照目标比例裁剪并缩放 '''
    global dst_w, dst_h, dst_path
    try:
        im = Image.open(str(fp))
    except (OSError, UnidentifiedImageError):
        print(f"无法识别的图像文件: {fp}")
        return
    src_w,src_h = im.size
    dst_scale = float(dst_h / dst_w) #目标高宽比
    src_scale = float(src_h / src_w) #原高宽比

    if src_scale >= dst_scale:
        #过高
        # print("原图过高")
        width = src_w
        height = int(width*dst_scale)
        x = 0
        y = (src_h - height) / 2

    else:
        #过宽
        # print("原图过宽\n")
        height = src_h
        width = int(height/dst_scale)
        x = (src_w - width) / 2
        y = 0
        
    #裁剪
    box = (x,y,width+x,height+y)
    
    #这里的参数可以这么认为：从某图的(x,y)坐标开始截，截到(width+x,height+y)坐标
    newIm = im.crop(box)
    im = None
    #压缩
    ratio = float(dst_w) / width
    newWidth = int(width * ratio)
    newHeight = int(height * ratio)
    dst_file = dst_path/fp.name  # 保持原文件名
    
    om = newIm.resize((newWidth, newHeight), resize_algorithm)
    
    # 计算图像质量指标
    # ssim_value, mse, psnr = calculate_metrics(np.array(im), np.array(om))
    # print(f'{fp.name}: SSIM={ssim_value:.4f}, MSE={mse:.4f}, PSNR={psnr:.4f}')

    # 保存生成图像
    dst_file = dst_path / f"{fp.stem}_{dst_w}x{dst_h}_{fp.name}"
    om.save(dst_file, quality=100)

    # return ssim_value, mse, psnr
    
def get_src_path():
    src_dir = input('请输入图片文件夹位置(输入Q或q退出):')
    if src_dir == "Q" or src_dir == 'q':
        sys.exit()
    src_path = Path(src_dir)
    src_path = src_path.expanduser()
    print("输入的文件夹：",src_path)
    return src_path

def get_resize_algorithm():
    print("请选择缩放算法:")
    for key, value in resampling_options.items():
        print(f"{key}. {value.name} (默认)" if value == resize_algorithm else f"{key}. {value.name}")

    choice = input("请输入选项编号: ").strip()

    return resampling_options.get(choice, resize_algorithm)

def main():
    global src_path, dst_path, filecount
    src_path = get_src_path()

    resize_algorithm = get_resize_algorithm()
    print(f'选择的缩放算法: {resize_algorithm}')

    while (not src_path.exists()):
        print(f'文件夹{src_path}不存在，请检查输入的文件夹名称是否正确。')
        src_path = get_src_path()

    algorithm_name = resize_algorithm.name.lower()
    dst_dir = f'{src_path}_{algorithm_name}_{dst_w}x{dst_h}'
    dst_path = Path(dst_dir)

    filecount = 0
    # 此参数规定了最后文件列表每行显示的文件名数量。
    display_each_line = 10

    cnt = 0
    # print('原始图片文件夹:',src_path)
    print('目标文件夹:',dst_path)
    if dst_path.exists():
        print(f'目标文件夹 {dst_path} 已经存在...')
        pass
    else:
        # print(f'创建目标文件夹: {dst_path} ')
        dst_path.mkdir(parents=True)

    print(f'目标分辨率:{dst_w}x{dst_h}')
    resize_dir_images(src_path)
    remove_ds_store(dst_path)
    # dst_file_list = dst_path.iterdir() # 
    # 直接遍历目标文件夹下的jpg/jpeg文件(使用*.jp*g来匹配两种后缀名)。
    dst_file_list = dst_path.glob('*.jp*g')
    print(f'\n一共转换了{filecount}个文件\n已转换的文件列表：',end='')
    line_count = 0
    for f in sorted(dst_file_list, key = lambda f : f.stem):
        cnt += 1
        if cnt%display_each_line == 1:
            line_count += 1
            print('\n%d | %10s'%(line_count,f.name),end='')
        else:
            print('%10s'%f.name,end='')

if __name__ == '__main__':
    main()
