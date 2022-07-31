'''
created at 24/07/22

@author: Assaf S.
'''
from ctypes import (
    c_short,
    c_int,
    c_char_p,
    byref,
    c_uint,
)
from time import sleep

from thorlabs_kinesis import benchtop_stepper_motor as bsm

# Global Parameters
STEP = 1.2207020447709976e-06 #device unit in [mm]

class Stepper_Control():
       """
       This module controls the Thorlab's Benchtop StepperMotor, using dll's bindings.
       """

       def __init__(self,Serial_Number = '70284354',Print_Detailed_Info = False):
            """"""
            self.c_Serial_Number = c_char_p(bytes(Serial_Number, "utf-8"))
            if bsm.TLI_BuildDeviceList() == 0:
                if bsm.SBC_Open(self.c_Serial_Number) == 0:
                    device_info = bsm.TLI_DeviceInfo()  # container for device info
                    bsm.TLI_GetDeviceInfo(self.c_Serial_Number, byref(device_info))
                    print("Stepper Motor",device_info.serialNo, "is connected")
                    if(Print_Detailed_Info == True):
                        print("Description: ", device_info.description)
                        print("Serial No: ", device_info.serialNo)
                        print("Motor Type: ", device_info.motorType)
                        print("USB PID: ", device_info.PID)
                        print("Max Number of  Channels: ", device_info.maxChannels)
                else:
                    print("could'nt connect to device, error number:", bsm.SBC_Open(self.c_Serial_Number), " 1 - FT_InvalidHandle - The FTDI functions have not been initialized.\n 2- "
                            "FT_DeviceNotFound - The Device could not be found This can be generated if the function TLI_BuildDeviceList() has not been called.\n  3- FT_DeviceNotOpened - The Device must be opened before it can be accessed" 
                            "See the appropriate Open function for your device.\n For more info check C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.C_API ")
            else:
                print("could'nt find device list, device not connected, error number:",bsm.TLI_BuildDeviceList(), " 1 - FT_InvalidHandle - The FTDI functions have not been initialized.\n 2- "
                            "FT_DeviceNotFound - The Device could not be found This can be generated if the function TLI_BuildDeviceList() has not been called.\n  3- FT_DeviceNotOpened - The Device must be opened before it can be accessed" 
                            "See the appropriate Open function for your device.\n For more info check C:\Program Files\Thorlabs\Kinesis\Thorlabs.MotionControl.C_API ")

       def __del__(self):
           bsm.SBC_Close(self.c_Serial_Number)
           print("Stopping polling ", bsm.SBC_StopPolling(self.c_Serial_Number,self.c_Channel))
           print("Closing connection ", bsm.SBC_Close(self.c_Serial_Number, self.c_Channel))

       def Polling_and_Queue_Stepper(self,c_Milliseconds =100):
           '''
            Starts the internal polling loop which continuously requests position and status.
           :param c_Milliseconds: The milliseconds polling rate.
           :return:
           '''
           print("Starting polling ", bsm.SBC_StartPolling(self.c_Serial_Number, self.c_Channel, c_Milliseconds))
           bsm.SBC_ClearMessageQueue(self.c_Serial_Number, self.c_Channel)


       def Jog(self,Channel=1,Step_Size = int(1e8),Accelaration = int(1e8), Max_Velocity=int(1e8),Jog_Direction='Forwards'):
           '''
           Jog the stage with definite step size towrads a specific direction.
           :param Channel: Stepper's Channel
           :param Step_Size:
           :param Accelaration:
           :param Max_Velocity:
           :param Jog_Direction:
           :return:
           '''
           #parameters
           self.c_Channel = c_short(Channel)

           #polling and queue
           sleep(0.2)
           self.Polling_and_Queue_Stepper()

           #setting jog params
           sleep(0.2)
           bsm.SBC_SetJogMode(self.c_Serial_Number, self.c_Channel,c_short(1),c_short(2))
           Current_Jog_Mode = c_short()
           Current_Jog_Stop_Mode = c_short()
           bsm.SBC_GetJogMode(self.c_Serial_Number, self.c_Channel,byref(Current_Jog_Mode),byref(Current_Jog_Stop_Mode))

           bsm.SBC_SetJogStepSize(self.c_Serial_Number, self.c_Channel, c_uint(Step_Size))
           print("Jog step size set to ",
                 bsm.SBC_GetJogStepSize(self.c_Serial_Number, self.c_Channel))
           sleep(0.2)

           bsm.SBC_SetJogVelParams(self.c_Serial_Number, self.c_Channel, c_int(Accelaration), c_int(Max_Velocity))
           c_acceleration = c_int()  # container
           c_maxVelocity = c_int()  # container
           bsm.SBC_RequestJogParams(self.c_Serial_Number, self.c_Channel)
           bsm.SBC_GetJogVelParams(self.c_Serial_Number, self.c_Channel, byref(c_acceleration),
                                   byref(c_maxVelocity))
           print("Jog max velocity is set to",c_maxVelocity.value,"acceleration",c_acceleration.value)

           sleep(0.2)


           # activating jogging
           if Jog_Direction == 'Forwards':
               bsm.SBC_MoveJog(self.c_Serial_Number, self.c_Channel, bsm.MOT_Forwards)
               print(f"Moving {Step_Size} Forwards")
           elif Jog_Direction == 'Backwards':
               print(f"Moving {Step_Size} Backwards")
               bsm.SBC_MoveJog(self.c_Serial_Number, self.c_Channel, bsm.MOT_Reverse)
           sleep(0.2)
           #must exist - without it the stage will keep moving!!
           bsm.SBC_StopProfiled(self.c_Serial_Number, self.c_Channel)
           # print current position
           sleep(0.2)
           position = int(bsm.SBC_GetPosition(self.c_Serial_Number, self.c_Channel))
           sleep(0.2)
           print(f"Current pos: {position}")

           # print("Stopping polling ", bsm.SBC_StopPolling(self.c_Serial_Number, self.c_Channel))
           # print("Closing connection ", bsm.SBC_Close(self.c_Serial_Number, self.c_Channel))

       def Home_Stepper(self,Channel=1,Milliseconds = 100,Homing_Velocity =1):
           '''
           This function is not yet ready to use!!!
           :param Channel:
           :param Milliseconds:
           :param Homing_Velocity:
           :return:
           '''
           # #homing parameters setting
           self.c_Channel = c_short(Channel)
           c_Milliseconds = c_int(Milliseconds)

           # homing_inf = bsm.MOT_HomingParameters()  # container
           #
           # print("Setting homing vel ", bsm.SBC_SetHomingVelocity(self.c_Serial_Number,c_Channel, bsm.c_uint(Homing_Velocity)))
           #
           # bsm.SBC_RequestHomingParams(self.c_Serial_Number,c_Channel)
           # err = bsm.SBC_GetHomingParamsBlock(self.c_Serial_Number,c_Channel, byref(homing_inf))
           # if err == 0:
           #     print("Direction: ", homing_inf.direction)
           #     print("Limit Sw: ", homing_inf.limitSwitch)
           #     print("Velocity: ", homing_inf.velocity)
           #     print("Offset Dist: ", homing_inf.offsetDistance)
           #
           # else:
           #     print(f"Error getting Homing Info Block. Error Code: {err}")
           #

           # homing operation
           sleep(1.0)
           bsm.SBC_StartPolling(self.c_Serial_Number, self.c_Channel, c_Milliseconds)
           bsm.SBC_ClearMessageQueue(self.c_Serial_Number, self.c_Channel)
           sleep(1.0)

           err = bsm.SBC_Home(self.c_Serial_Number, Channel)
           sleep(1.0)
           if err == 0:
               while True:
                   current_position = int(bsm.SBC_GetPosition(self.c_Serial_Number, Channel))
                   if current_position == 0:
                       print("At home.")
                       break
                   else:
                       print(f"Homing...{current_position}")

                   sleep(1.0)
           else:
               print(f"Can't home. Err: {err}")
           bsm.SBC_StopPolling(self.c_Serial_Number, Channel)



       def Move_To_Absulote_Position_Stepper(self, Channel=1, Milliseconds=100,Move_To = 800):
           #moving the stage parameters setting
           self.c_Channel = c_short(Channel)
           c_Milliseconds = c_int(Milliseconds)

           velocity_inf = bsm.MOT_VelocityParameters()  # container
           velocity_inf.maxVelocity = c_int(3)
           print(velocity_inf)
           #
           print("Setting step velocity ", bsm.SBC_SetVelParamsBlock(self.c_Serial_Number,self.c_Channel,byref(velocity_inf)))
           #
           # bsm.SBC_RequestHomingParams(self.c_Serial_Number,c_Channel)
           # err = bsm.SBC_GetHomingParamsBlock(self.c_Serial_Number,c_Channel, byref(homing_inf))
           # if err == 0:
           #     print("Direction: ", homing_inf.direction)
           #     print("Limit Sw: ", homing_inf.limitSwitch)
           #     print("Velocity: ", homing_inf.velocity)
           #     print("Offset Dist: ", homing_inf.offsetDistance)
           #
           # else:
           #     print(f"Error getting Homing Info Block. Error Code: {err}")
           #

           # moving the stage operation


           print("Starting polling ", bsm.SBC_StartPolling(self.c_Serial_Number, self.c_Channel, c_Milliseconds))
           print("Clearing message queue ", bsm.SBC_ClearMessageQueue(self.c_Serial_Number, self.c_Channel))
           sleep(0.2)

           print("Setting Absolute Position ",
                 bsm.SBC_SetMoveAbsolutePosition(self.c_Serial_Number, self.c_Channel, c_int(Move_To)))
           sleep(0.2)

           print(f"Moving to {Move_To}", bsm.SBC_MoveAbsolute(self.c_Serial_Number, self.c_Channel))
           sleep(0.2)
           position = int(bsm.SBC_GetPosition(self.c_Serial_Number, self.c_Channel))
           sleep(0.2)
           print(f"Current pos: {position}")
           while not position == Move_To:
               sleep(0.2)
               position = int(bsm.SBC_GetPosition(self.c_Serial_Number, self.c_Channel))
               print(f"Current pos: {position}")

           print("Stopping polling ", bsm.SBC_StopPolling(self.c_Serial_Number, self.c_Channel))
           print("Closing connection ", bsm.SBC_Close(self.c_Serial_Number, self.c_Channel))


if __name__ == "__main__":
    o=Stepper_Control()
    # o.Move_To_Absulote_Position_Stepper()
    o.Jog()
