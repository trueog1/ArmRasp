#!/usr/bin/python3
# encoding: utf-8
# 配置串口舵机的参数
# 每次只能配置一个舵机，且扩展板只能连接一个舵机，既是一个舵机一个舵机配置参数
from SerialServoCmd import *
import timeout_decorator

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_set_id(oldid, newid):
    """
    配置舵机id号, 出厂默认为1
    :param oldid: 原来的id， 出厂默认为1
    :param newid: 新的id
    """
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_ID_WRITE, newid)

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_id(id=None):
    """
    读取串口舵机id
    :param id: 默认为空
    :return: 返回舵机id
    """
    while True:
        if id is None:  # 总线上只能有一个舵机
            serial_servo_read_cmd(0xfe, LOBOT_SERVO_ID_READ)
        else:
            serial_servo_read_cmd(id, LOBOT_SERVO_ID_READ)
        # 获取内容
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ID_READ)
        if msg is not None:
            return msg

def serial_servo_stop(id=None):
    '''
    停止舵机运行
    :param id:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_MOVE_STOP)

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_set_deviation(id, d=0):
    """
    配置偏差，掉电保护
    :param id: 舵机id
    :param d:  偏差
    """
    # 设置偏差
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_ADJUST, d)
    # 设置为掉电保护
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_WRITE)

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_deviation(id):
    '''
    读取偏差值
    :param id: 舵机号
    :return:
    '''
    # 发送读取偏差指令
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_ANGLE_OFFSET_READ)
        # 获取
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ANGLE_OFFSET_READ)
        if msg is not None:
            return msg

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_set_angle_limit(id, low, high):
    '''
    设置舵机转动范围
    :param id:
    :param low:
    :param high:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_ANGLE_LIMIT_WRITE, low, high)

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_angle_limit(id):
    '''
    读取舵机转动范围
    :param id:
    :return: 返回元祖 0： 低位  1： 高位
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_ANGLE_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_ANGLE_LIMIT_READ)
        if msg is not None:
            return msg

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_set_vin_limit(id, low, high):
    '''
    设置舵机电压范围
    :param id:
    :param low:
    :param high:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_VIN_LIMIT_WRITE, low, high)

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_vin_limit(id):
    '''
    读取舵机转动范围
    :param id:
    :return: 返回元祖 0： 低位  1： 高位
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_VIN_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_VIN_LIMIT_READ)
        if msg is not None:
            return msg

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_set_max_temp(id, m_temp):
    '''
    设置舵机最高温度报警
    :param id:
    :param m_temp:
    :return:
    '''
    serial_serro_wirte_cmd(id, LOBOT_SERVO_TEMP_MAX_LIMIT_WRITE, m_temp)

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_temp_limit(id):
    '''
    读取舵机温度报警范围
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_TEMP_MAX_LIMIT_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_TEMP_MAX_LIMIT_READ)
        if msg is not None:
            return msg

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_pos(id):
    '''
    读取舵机当前位置
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_POS_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_POS_READ)
        if msg is not None:
            return msg

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_temp(id):
    '''
    读取舵机温度
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_TEMP_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_TEMP_READ)
        if msg is not None:
            return msg

@timeout_decorator.timeout(3, use_signals=False)
def serial_servo_read_vin(id):
    '''
    读取舵机电压
    :param id:
    :return:
    '''
    while True:
        serial_servo_read_cmd(id, LOBOT_SERVO_VIN_READ)
        msg = serial_servo_get_rmsg(LOBOT_SERVO_VIN_READ)
        if msg is not None:
            return msg

def serial_servo_rest_pos(oldid):
    # 舵机清零偏差和P值中位（500）
    serial_servo_set_deviation(oldid, 0)    # 清零偏差
    time.sleep(0.1)
    serial_serro_wirte_cmd(oldid, LOBOT_SERVO_MOVE_TIME_WRITE, 500, 100)    # 中位

@timeout_decorator.timeout(3, use_signals=False)
##掉电
def serial_servo_load_or_unload_write(id):
    serial_serro_wirte_cmd(id, LOBOT_SERVO_LOAD_OR_UNLOAD_WRITE, 0)

@timeout_decorator.timeout(3, use_signals=False)
##读取是否掉电
def serial_servo_load_or_unload_read(id):
    serial_servo_read_cmd(id, LOBOT_SERVO_LOAD_OR_UNLOAD_READ)
    while True:
        msg = serial_servo_get_rmsg(LOBOT_SERVO_LOAD_OR_UNLOAD_READ)
        if msg is not None:
            return msg
        
def show_servo_state():
    '''
    显示信息
    :return:
    '''
    oldid = serial_servo_read_id()
    portRest()
    if oldid is not None:
        print('当前的舵机ID是：%d' % oldid)
        pos = serial_servo_read_pos(oldid)
        print('当前的舵机角度：%d' % pos)
        portRest()

        now_temp = serial_servo_read_temp(oldid)
        print('当前的舵机温度：%d°' % now_temp)
        portRest()

        now_vin = serial_servo_read_vin(oldid)
        print('当前的舵机电压：%dmv' % now_vin)
        portRest()

        d = serial_servo_read_deviation(oldid)
        print('当前的舵机偏差：%d' % ctypes.c_int8(d).value)
        portRest()

        limit = serial_servo_read_angle_limit(oldid)
        print('当前的舵机可控角度为%d-%d' % (limit[0], limit[1]))
        portRest()

        vin = serial_servo_read_vin_limit(oldid)
        print('当前的舵机报警电压为%dmv-%dmv' % (vin[0], vin[1]))
        portRest()

        temp = serial_servo_read_temp_limit(oldid)
        print('当前的舵机报警温度为50°-%d°' % temp)
        portRest()

    return oldid

if __name__ == '__main__':
    show_servo_state()