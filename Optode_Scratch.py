# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 11:00:10 2016

@author: Yaqub
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 14:53:46 2016

@author: fred
"""

import h5py
import DAQT7_Objective as DAQ
import SeaBreeze_Objective as SBO
import ThorlabsPM100_Objective as P100
import time
#import datetime
import numpy as np
from multiprocessing import Process, Value, Array
import matplotlib.pyplot as plt
import os.path

time_start =  time.time()

# ######################### Naming the DAQ ports ##########################
# FIO0 = shutter of the green laser and FIO1 is the shutter of the blue laser
# FIO2 = is the green laser and the FIO3 is the blue laser
# Green_Laser = "FIO1"
Green_Shutter = "DAC0"
# Blue_Laser = "FIO0"
Blue_Shutter = "FIO2"

PhotoDiod_Port = "AIN1"
#Spectrometer_Trigger_Port = "DAC0"


# ####################### Interrupt like delays (s) ####################### '''
# Usage Ex: Px = Process(target=Timer_Multi_Process, args=(Timer_time,))
# Px.start() and in your code constantly check for "Timer_Is_Done"

def Timer_Multi_Process(Time_In_Seconds):
    if Timer_Is_Over.value is 1:
        print 'Error: This timer can be called one at a time. The previous timer is still running'
    time.sleep(Time_In_Seconds)
    Timer_Is_Over.value = 1
    

# ######## A function for reading the DAQ analogue inpute and command signals to other ports ########

def DAQ_Read_Process(No_DAC_Sample,):
    I = 0
    while I < 10:
        DAQ_Index[0] = 0
        DAQ1.writePort(Shutter_Port, 0)
        Ref_Time[DAQ_Index_Total[0]] = time.time()
        State = -1        
        while DAQ_Index[0] < No_DAC_Sample:
            DAQ_Signal[DAQ_Index_Total[0]], DAQ_Time[DAQ_Index_Total[0]] = DAQ1.readPort(PhotoDiod_Port)
            #Ref_Signal[DAQ_Index_Total[0]] = 0
            DAQ_Index[0] = DAQ_Index[0] + 1
            DAQ_Index_Total[0] = DAQ_Index_Total[0] + 1
            Ref_Time[DAQ_Index_Total[0]] = time.time()
        I = I + 1 
        print (I)
        print (time.time())

        DAQ_Index[0] = 0
        DAQ1.writePort(Shutter_Port, 5)
        Ref_Time[DAQ_Index_Total[0]] = time.time()
        State = 1
        while DAQ_Index[0] < No_DAC_Sample - 1:
            DAQ_Signal[DAQ_Index_Total[0]], DAQ_Time[DAQ_Index_Total[0]] = DAQ1.readPort(PhotoDiod_Port)
            Ref_Signal[DAQ_Index_Total[0]] = 1
            DAQ_Index[0] = DAQ_Index[0] + 1
            DAQ_Index_Total[0] = DAQ_Index_Total[0] + 1
            Ref_Time[DAQ_Index_Total[0]] = time.time()
        I = I + 1    
        print (I)
        print (time.time())
    DAQ1.writePort(Shutter_Port, 0)
    DAQ_Is_Read.value = 1
    

# ######## A function for reading the Power meter ########
def Power_Read_Process(No_Power_Sample):
    Power_Is_Read.value = 1


    
    
# # A function for initializing the spectrometer (integration time and triggering mode '''
def Spec_Init_Process(Integration_Time, Trigger_mode):
    #print 'Spectrometer is initialized'
    Spec1.setTriggerMode(Trigger_mode)
    time.sleep(0.01)
    print (Integration_Time)
    Spec1.setIntegrationTime(Integration_Time*1000)
    time.sleep(0.01)
    Spec_Init_Done.value = 1
    
# ########## A function for reading the spectrometer intensities ########### '''
def Spec_Read_Process(No_Spec_Sample):
    Current_Spec_Record[:], Spec_Time[Spec_Index[0]]  = Spec1.readIntensity(True, True)
    Spec_Is_Read.value = 1
    #Spec_Index[0] = Spec_Index[0] + 1
    print "spectrometer Index is %i" % Spec_Index[0]


def MultiIntegrationParadigm(Integration_list_sec, Delay_Between_Integrations, Shutter_Delay):
    Trigger_mode = 3                # External edge trigger  
    OrderOfTheProcess = 0 
    Spec_Init_Done.value = 0 
    Pros_Spec_Init = Process(target = Spec_Init_Process, args=(Integration_list_sec[Spec_Index[0]], Trigger_mode))
    Pros_Spec_Init.start()    
    print ('Step1')
    Timer_Is_Over.value = 0
    while Spec_Index[0] < len(Integration_list_sec):
        if  (Spec_Init_Done.value == 1) & (OrderOfTheProcess == 0): 
            Spec_Init_Done.value = 0
            print ('Step2')
            Pros_Spec = Process(target=Spec_Read_Process, args=(1,))
            Pros_Spec.start()
            print ('Step3')
            Timer_Is_Over.value = 0
            #P_Timer = Process(target=Timer_Multi_Process, args=((Integration_list_sec[Spec_Index[0]])/float(1000),)) 
            P_Timer = Process(target=Timer_Multi_Process, args=((Integration_list_sec[Spec_Index[0]] - Shutter_Delay/float(3))/float(1000),)) 
            P_Timer.start()
            
            DAQ1.writePort(Shutter_Port, 5)
            print ('Step4')
            Ref_Time[DAQ_Index[0]] = time.time()
            OrderOfTheProcess = 1
        elif(Timer_Is_Over.value == 1) & (OrderOfTheProcess ==1):
            print ('Step5')
            DAQ1.writePort(Shutter_Port, 0)
            Timer_Is_Over.value = 0
            #Ref_Time[DAQ_Index[0]] = time.time()
            #Spec_Index[0] = Spec_Index[0]  + 1
            OrderOfTheProcess = 2
        elif(Spec_Is_Read.value == 1) & (OrderOfTheProcess == 2):
            print ('Step6')
            Spec_Is_Read.value = 0
            Full_Spec_Records[:, np.int(Spec_Index[0])] = Current_Spec_Record[:]
            Pros_Spec_Init = Process(target = Spec_Init_Process, args=(Integration_list_sec[Spec_Index[0]], Trigger_mode))
            Pros_Spec_Init.start()
            Spec_Index[0] = Spec_Index[0]  + 1
            OrderOfTheProcess = 0
        
            
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        #print (DAQ_Signal[DAQ_Index[0]])
        DAQ_Index[0] = DAQ_Index[0] + 1
        #Ref_Time[DAQ_Index[0]] = time.time()
    Pros_Spec.terminate()
    
    
    Timer_Is_Over.value = 0            
    P_Timer = Process(target=Timer_Multi_Process, args=(0.1,)) 
    P_Timer.start()
    while  Timer_Is_Over.value == 0:    
        DAQ_Signal[DAQ_Index[0]], DAQ_Time[DAQ_Index[0]] = DAQ1.readPort(PhotoDiod_Port)
        #print (DAQ_Signal[DAQ_Index[0]])
        DAQ_Index[0] = DAQ_Index[0] + 1
        #Ref_Time[DAQ_Index[0]] = time.time()

if __name__ == "__main__":
    
    while 1==1:
        Current_Laser = raw_input('Which laser you want? Press G for green laser or press B for blue laser and then press Enter:')
        if (Current_Laser == 'G') | (Current_Laser == 'g'):
            #Laser_Port = Green_Laser
            Shutter_Port = Green_Shutter
            break
        elif (Current_Laser == 'B') | (Current_Laser == 'b'):
            #Laser_Port = Blue_Laser
            Shutter_Port = Blue_Shutter
            break
        else:
            print 'Wrong input!'
    
    
    Spec1 = SBO.DetectSpectrometer()
    Integration_Time = 100                                        # Integration time in ms
    Spec1.setTriggerMode(0)                                      # It is set for free running mode
    Spec1.setIntegrationTime(Integration_Time*1000)              # Integration time is in microseconds when using the library
    
    DAQ1 = DAQ.DetectDAQT7()
    DAQ1.writePort(Green_Shutter, 0)
    DAQ1.writePort(Blue_Shutter, 0)


    time.sleep(0.1)
    
    #Power_meter = P100.DetectPM100D()
    
    Spec_Is_Read = Value('i', 0)
    Spec_Is_Read.value = 0
    Spec_Init_Done = Value('i',0)
    Spec_Init_Done.value = 0 

    DAQ_Is_Read = Value('i', 0)
    DAQ_Is_Read.value = 0

    Power_Is_Read = Value('i', 0)
    Power_Is_Read.value = 0

    Timer_Is_Over = Value('i', 0)
    Timer_Is_Over.value = 0

    
    # ##################### Initializing the variables ###################
    Integration_list_sec = [8, 16, 32, 64, 128, 256, 512, 1024 ]    #Integration time for the spectrometer in ms
    Shutter_Delay = 4    #ms
    DAQ_SamplingRate = 0.4         #ms
    Powermeter_SamplingRate = 5.1     #ms
    Delay_Between_Integrations = 100  #ms
    DurationOfReading = np.sum(Integration_list_sec)  + len(Integration_list_sec)*Delay_Between_Integrations   # Duration of reading in seconds.
    No_DAC_Sample =   int(round(DurationOfReading/DAQ_SamplingRate))        # Number of samples for DAQ analogue to digital converter (AINx). 
                                                                            # Roughly DAQ can read AINx 0.4
    No_Power_Sample = int(round(DurationOfReading/Powermeter_SamplingRate)) # Number of samples for P100D Power meter to read. 
                                                                            # Roughly P100 can read the power every 2.7 ms.
    #No_Spec_Sample =  int(round(DurationOfReading*1000/(Integration_Time)))# Number of samples for spectrometer to read. 
    No_Spec_Sample =  len(Integration_list_sec)                             # Number of samples for spectrometer to read. 
    
    
    Current_Spec_Record = Array('d', np.zeros(shape=( len(Spec1.Handle.wavelengths()) ,1), dtype = float ))
    Spec_Index = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    Full_Spec_Records = np.zeros(shape=(len(Spec1.Handle.wavelengths()), No_Spec_Sample ), dtype = float )
    Spec_Time   = Array('d', np.zeros(shape=( No_Spec_Sample ,1), dtype = float ))

    
    
    DAQ_Signal = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
    DAQ_Time   = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
    DAQ_Index  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    DAQ_Index_Total  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    Ref_Signal = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
    Ref_Time   = Array('d', np.zeros(shape=( No_DAC_Sample ,1), dtype = float ))
    '''
    Power_Signal = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
    Power_Time   = Array('d', np.zeros(shape=( No_Power_Sample ,1), dtype = float ))
    Power_Index  = Array('i', np.zeros(shape=( 1 ,1), dtype = int ))
    '''
    # ########### The file containing the records (HDF5 format)###########'''

    
    #Pros_DAQ = Process(target=DAQ_Read_Process, args=(No_DAC_Sample,))
    #Pros_DAQ.start()
    '''
    Pros_Power = Process(target=Power_Read_Process, args=(No_Power_Sample,))
    Pros_Power.start()
    Pros_Spec = Process(target=Spec_Read_Process, args=(No_Spec_Sample,))
    Pros_Spec.start()


    while((Spec_Is_Done.value == 0)):
        if  Spec_Is_Read.value == 1:
            Spec_Is_Read.value = 0
            Full_Spec_Records[:, np.int(Spec_Index[0])] = Current_Spec_Record[:]
    print('Spectrometer is done')
    '''
    
    '''
    II = 0 
    while (DAQ_Is_Read.value == 0):
        time.sleep(1)
        print (time.time())
        '''
    '''        
        try:
            time.sleep(1)
            print (time.time())
        except KeyboardInterrupt:
            break 
        '''
        
    MultiIntegrationParadigm(Integration_list_sec, Delay_Between_Integrations, Shutter_Delay)
    

    time.sleep(0.1)
    DAQ1.close()
    Spec1.close()

    # ######### Plotting the spectrumeter and the photodiod recordings ########
    plt.figure()
    plt.plot(np.asarray(DAQ_Time[0:DAQ_Index[0]]) - DAQ_Time[0],DAQ_Signal[0:DAQ_Index[0]])    
    #plt.plot(np.asarray(Ref_Time[0:DAQ_Index[0]]) - DAQ_Time[0],Ref_Signal[0:DAQ_Index[0]])
    
    '''   
    plt.subplot(1,3,1)
    #DAQ_Signal = np.asarray(DAQ_Signal[0:DAQ_Index_Total[0]])
    plt.plot(DAQ_Time[0:DAQ_Index_Total[0]], DAQ_Signal[0:DAQ_Index_Total[0]], label = "Photo Diode")
    plt.title('Photo diode')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (v)')
    '''
    '''
    plt.subplot(1,3,2)
    Power_Signal = np.asarray(Power_Signal[0:Power_Index[0]])
    plt.plot(Power_Time[0:Power_Index[0]], Power_Signal[0:Power_Index[0]], label = "Power meter")
    plt.title('Power meter')
    plt.xlabel('Time (s)')
    plt.ylabel('Pwor (w)')

    plt.subplot(1,3,3)
    plt.plot(Spec1.readWavelength()[1:],Full_Spec_Records[1:]);
    plt.title('Specrometer recordings')
    plt.xlabel('Wavelength (nano meter)')
    plt.ylabel('Intensity')
    plt.show()
    '''
    ################################Closing the devices#############################
    '''
    plt.figure()
    plt.plot(DAQ_Time, (DAQ_Signal[0:DAQ_Index_Total[0]]-np.mean(DAQ_Signal))/float( np.max(np.abs(DAQ_Signal))))
    #plt.plot(Power_Time, (Power_Signal[0:Power_Index[0]]-np.mean(Power_Signal))/float( np.max(np.abs(Power_Signal))))
    #plt.title("Super imposed Power and DAQ signals (not the actual signals)")
    plt.plot(Ref_Signal, (Ref_Signal[0:DAQ_Index_Total[0]]))
    
    plt.xlabel("Unix time")
    plt.legend(['DAQ', 'P100'])
    plt.show()
    '''

    #################### Estimate the latencies of the devices ###################################
    plt.figure()

    DAQ_Latency = DAQ_Time[0:DAQ_Index[0]]
    DAQ_Latency[0] = 0
    for I in range(1,DAQ_Index[0]):
        DAQ_Latency[I] = DAQ_Time[I] - DAQ_Time[I-1]
    plt.subplot(1,3,1)
    plt.plot(DAQ_Latency)
    plt.ylabel("Time (s)")
    plt.title("DAQ latencies")
    plt.show()
    '''
    Power_Latency = Power_Time[0:Power_Index[0]]
    Power_Latency[0] = 0
    for I in range(1,Power_Index[0]):
        Power_Latency[I] = Power_Time[I] - Power_Time[I-1]
    plt.subplot(1,3,2)
    plt.plot(Power_Latency)
    plt.title("P100 latencies")
    plt.ylabel("Time (s)")

    plt.subplot(1,3,3)
    Spec_Latency = Spec_Time[0:np.int(Spec_Index[0])]
    Spec_Latency[0] = 0
    for I in range(1,Spec_Index[0]):
        Spec_Latency[I] = np.float(Spec_Time[I] - Spec_Time[I-1])
    plt.plot(Spec_Latency)
    plt.ylabel("Time (s)")
    plt.title("Spectrometer integration durations")
    plt.show()
    '''    
    