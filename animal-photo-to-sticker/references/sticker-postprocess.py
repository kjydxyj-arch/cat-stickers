"""
AnimalPhoto2Sticker 配套后期脚本
功能：给透明底PNG自动添加 3~4px 均匀刀模白边 + 柔和贴纸投影
使用方法：python3 sticker_postprocess.py 输入图.png 输出图.png
依赖：pip install pillow
"""
import sys
from PIL import Image, ImageFilter


def add_sticker_border_shadow(input_path, output_path, border_px=4, shadow_blur=3):
    """
    给透明底图片添加贴纸白边和柔和投影。
    :param input_path: 输入透明底PNG路径
    :param output_path: 输出贴纸PNG路径
    :param border_px: 白边宽度（像素），印刷贴纸推荐 3~4
    :param shadow_blur: 阴影模糊半径
    """
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size

    # 1. 扩展画布，留出白边空间
    new_w = w + border_px * 2
    new_h = h + border_px * 2
    canvas = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    canvas.paste(img, (border_px, border_px), mask=img)

    # 2. 生成白色刀模轮廓
    alpha = canvas.split()[-1]
    white_edge = Image.new("RGBA", canvas.size, (255, 255, 255, 255))
    white_edge.putalpha(alpha)
    # 向外膨胀得到白边
    dilated_alpha = alpha
    for _ in range(border_px):
        dilated_alpha = dilated_alpha.filter(ImageFilter.MaxFilter(3))
    white_edge.putalpha(dilated_alpha)

    # 3. 柔和阴影
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 100))
    shadow_alpha = dilated_alpha.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
    shadow.putalpha(shadow_alpha)

    # 图层合并顺序：阴影 → 白边 → 原图
    final = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    final.paste(shadow, (2, 2), mask=shadow)
    final.paste(white_edge, (0, 0), mask=white_edge)
    final.paste(canvas, (0, 0), mask=canvas)

    final.save(output_path)
    print(f"✅ 贴纸已输出: {output_path}")
    print(f"   白边宽度: {border_px}px | 阴影模糊: {shadow_blur}px | 尺寸: {final.size[0]}x{final.size[1]}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 sticker_postprocess.py <输入图.png> <输出图.png> [白边px=4]")
        print("示例: python3 sticker_postprocess.py input.png sticker_output.png 4")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    border = int(sys.argv[3]) if len(sys.argv) > 3 else 4

    add_sticker_border_shadow(input_file, output_file, border_px=border)
