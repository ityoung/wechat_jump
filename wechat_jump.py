from PIL import Image
import math
import subprocess
import time
import io

# adb 截图命令
screen_catch_cmd = 'adb exec-out screencap -p'

jumper_color = (55, 55, 95)
shadow_color = (134, 138, 167)
background_color = (1, 1, 1)

screen_height = 1920
screen_width = 1080
jumper_min_y = 1000
jumper_max_y = 1400
jumper_offset_x = 15
jumper_offset_y = 17
jumper_height = 30
# x在截图左/右侧时对应的参数,用于计算目标方块y坐标
left_x_y = 1.82
right_x_y = 1.75
find_step = 5
time_distance = 1.35


def get_screeshoot(debug_image = None):
    '''
    获取游戏图片
    :param debug_image: 
    :return: image对象
    '''
    if debug_image:
        image = Image.open(debug_image)
        # print(image)
    else:
        process = subprocess.Popen(screen_catch_cmd.split(), stdout=subprocess.PIPE)
        image_data, error = process.communicate()
        image = Image.open(io.BytesIO(image_data))
    return image


def is_same_color(color1, color2, tolerance=30):
    '''
    判断两个像素点颜色相近/同
    :param color1: 
    :param color2: 
    :param tolerance: 颜色误差容忍范围
    :return: 相同返回 True, 否则 False
    '''
    return sum(abs(color1[index] - color2[index]) for index in range(3)) < tolerance


def find_jumper_center(pixel):
    '''
    寻找跳跃者中心点坐标
    :param pixel: 
    :return: 跳跃者中心点坐标
    '''
    for y in range(jumper_min_y, jumper_max_y, find_step):
        for x in range(1, screen_width, find_step):
            if is_same_color(pixel[x, y], jumper_color, tolerance=10):
                return x+jumper_offset_x, y+jumper_offset_y


def find_target_center(pixel, jumper_coordinate):
    '''
    寻找下次跳跃中心点坐标
    :param pixel: 
    :param jumper_coordinate: 
    :return: 下次跳跃中心点坐标
    '''
    if jumper_coordinate[0] > screen_width / 2:
        target_edge_x = 1
        find_target_step = find_step
        var_y = left_x_y
        x_offset = 2*jumper_offset_x
    else:
        target_edge_x = 1079
        find_target_step = -find_step
        var_y = right_x_y
        x_offset = -2*jumper_offset_x
    for x in range(target_edge_x, int(screen_width / 2), find_target_step):
        y = int(jumper_coordinate[1] - abs(x - jumper_coordinate[0]) / var_y)
        if find_useful_pixel(pixel[x, y]):
            return x + x_offset, y + jumper_offset_y
            # x + x_offset
            # double_x = 0
            # found_x = x - 5
            # print(found_x, y)
            # while find_useful_pixel(pixel[found_x, y]):
            #     found_x -= 5
            # double_x += found_x
            # found_x = x + 5
            # while find_useful_pixel(pixel[found_x, y]):
            #     found_x += 5
            # double_x += found_x
            # return double_x / 2, y + jumper_offset_y
    # TODO: 更精确的定位计算


def find_useful_pixel(color):
    '''
    判断传入颜色是否不为背景色/阴影色
    :param color: 
    :return: 
    '''
    return not is_same_color(color, shadow_color) and not is_same_color(color, background_color)


def get_press_time(jumper_coordinate, target_coordinate):
    '''
    根据跳跃者坐标与目标方块坐标, 计算长按时间
    :param jumper_coordinate: 
    :param target_coordinate: 
    :return: 长按时间
    '''
    distance = math.sqrt((jumper_coordinate[0] - target_coordinate[0])**2+(jumper_coordinate[1]-target_coordinate[1])**2)
    press_time = time_distance * distance
    return press_time


def press(press_time):
    '''
    执行adb命令控制长按
    :param press_time: 
    :return: 
    '''
    press_command = 'adb shell input touchscreen swipe 170 187 170 187 {}'.format(int(press_time))
    process = subprocess.Popen(press_command.split(), stdout=subprocess.PIPE)
    process.communicate()


def jump(pixel):
    '''
    寻找坐标并执行长按操作
    :param pixel: 
    :return: 
    '''
    jumper_coordinate = find_jumper_center(pixel)
    target_coordinate = find_target_center(pixel, jumper_coordinate)
    press_time = get_press_time(jumper_coordinate, target_coordinate)
    press(press_time)


if __name__ == '__main__':
    try:
        while True:
            image = get_screeshoot()
            pixel = image.load()
            background_color = pixel[540, 300]
            jump(pixel)
            time.sleep(1)   # 避免跳跃过程中截图
    except KeyboardInterrupt:
        print("END JUMPING")
