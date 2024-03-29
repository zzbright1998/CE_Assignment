# manualTemplate.py
# A script to perform a template attack
# Will attack one subkey of AES-128

import numpy as np
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt

# Useful utilities
sbox=(
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16) 
hw = [bin(x).count("1") for x in range(256)]

def cov(x, y):
    # Find the covariance between two 1D lists (x and y).
    # Note that var(x) = cov(x, x)
    return np.cov(x, y)[0][1]


# Uncomment to check
#print sbox
#print [hw[s] for s in sbox]


# Start calculating template
# 1: load data
tempTraces = np.load('./train/traces.npy')
tempPText  = np.load('./train/textin.npy')
tempKey    = np.load('./train/keylist.npy')

#print tempPText
#print len(tempPText)
#print tempKey
#print len(tempKey)
#plt.plot(tempTraces[0])
#plt.show()
atkTraces = np.load("./test/2019.04.03-14.47.53_traces.npy")
resultMatrix = np.zeros((len(atkTraces), 16))
for dig in range(16):
    # 2: Find HW(sbox) to go with each input
    # Note - we're only working with the first byte here
    tempSbox = [sbox[tempPText[i][dig] ^ tempKey[i][dig]] for i in range(len(tempPText))] 
    tempHW   = [hw[s] for s in tempSbox]

    #print tempSbox
    #print tempHW


    # 2.5: Sort traces by HW
    # Make 9 blank lists - one for each Hamming weight
    tempTracesHW = [[] for _ in range(9)]

    # Fill them up
    for i in range(len(tempTraces)):
        HW = tempHW[i]
        tempTracesHW[HW].append(tempTraces[i])

    # Switch to numpy arrays
    tempTracesHW = [np.array(tempTracesHW[HW]) for HW in range(9)]

    #print len(tempTracesHW[8])


    # 3: Find averages
    tempMeans = np.zeros((9, len(tempTraces[0])))
    for i in range(9):
        tempMeans[i] = np.average(tempTracesHW[i], 0)
        
    #plt.plot(tempMeans[2])
    #plt.grid()
    #plt.show()


    # 4: Find sum of differences
    tempSumDiff = np.zeros(len(tempTraces[0]))
    for i in range(9):
        for j in range(i):
            tempSumDiff += np.abs(tempMeans[i] - tempMeans[j])

    # plt.plot(tempSumDiff)
    # plt.grid()
    # plt.show()


    # 5: Find POIs
    POIs = []
    numPOIs = 5
    POIspacing = 5
    for i in range(numPOIs):
        # Find the max
        nextPOI = tempSumDiff.argmax()
        POIs.append(nextPOI)
        
        # Make sure we don't pick a nearby value
        poiMin = max(0, nextPOI - POIspacing)
        poiMax = min(nextPOI + POIspacing, len(tempSumDiff))
        for j in range(poiMin, poiMax):
            tempSumDiff[j] = 0
    # print (POIs)
    '''

    '''
    # 6: Fill up mean and covariance matrix for each HW
    meanMatrix = np.zeros((9, numPOIs))
    covMatrix  = np.zeros((9, numPOIs, numPOIs))
    for HW in range(9):
        for i in range(numPOIs):
            # Fill in mean
            meanMatrix[HW][i] = tempMeans[HW][POIs[i]]
            for j in range(numPOIs):
                x = tempTracesHW[HW][:,POIs[i]]
                y = tempTracesHW[HW][:,POIs[j]]
                covMatrix[HW,i,j] = cov(x, y)
            
    #print meanMatrix
    #print covMatrix[0]


    # Template is ready!
    # 1: Load attack traces
    atkTraces = np.load("./test/2019.04.03-14.47.53_traces.npy")
    atkPText  = np.load("./test/2019.04.03-14.47.53_textin.npy")
    atkKey    = np.load("./test/2019.04.03-14.47.53_keylist.npy")

    #print atkTraces
    #print atkPText
    print (atkKey)


    # 2: Attack
    # Running total of log P_k
    
    P_k = np.zeros(256)
    for j in range(len(atkTraces)):
        # Grab key points and put them in a small matrix
        a = [atkTraces[j][POIs[i]] for i in range(len(POIs))]#a是降维之后的曲线
        
        # Test each key
        for k in range(256):
            # Find HW coming out of sbox
            HW = hw[sbox[atkPText[j][dig] ^ k]]
        
            # Find p_{k,j}
            rv = multivariate_normal(meanMatrix[HW], covMatrix[HW])
            p_kj = rv.pdf(a)
    
            # Add it to running total
            P_k[k] += np.log(p_kj)

        # Print our top 5 results so far
        # Best match on the right
        # for i in P_k:
        #     print(hex(int(i)))
        # print (P_k.argsort()[-5:])
        print (P_k.argsort()[-1:][0])
        resultMatrix[j][dig] = int(P_k.argsort()[-1:][0])
    print(resultMatrix)

def rate(result_list, correct_list):
    num = 0
    correctness = 0
    for i in range(len(result_list)):
        if result_list[i] == correct_list[i]:
            num = num+1
    correctness = num/len(result_list)

    return correctness

correctness_list = []
for i in range(len(resultMatrix)):
    # print(resultMatrix[i])
    # print(atkKey)
    data = rate(resultMatrix[i], atkKey[0])
    data = data*100
    correctness_list.append(data)

print(correctness_list)

plt.plot(correctness_list)
plt.grid()
plt.show()



















# # 2: Find HW(sbox) to go with each input
# # Note - we're only working with the first byte here
# tempSbox = [sbox[tempPText[i][3] ^ tempKey[i][3]] for i in range(len(tempPText))] 
# tempHW   = [hw[s] for s in tempSbox]

# #print tempSbox
# #print tempHW


# # 2.5: Sort traces by HW
# # Make 9 blank lists - one for each Hamming weight
# tempTracesHW = [[] for _ in range(9)]

# # Fill them up
# for i in range(len(tempTraces)):
#     HW = tempHW[i]
#     tempTracesHW[HW].append(tempTraces[i])

# # Switch to numpy arrays
# tempTracesHW = [np.array(tempTracesHW[HW]) for HW in range(9)]

# #print len(tempTracesHW[8])


# # 3: Find averages
# tempMeans = np.zeros((9, len(tempTraces[0])))
# for i in range(9):
#     tempMeans[i] = np.average(tempTracesHW[i], 0)
    
# #plt.plot(tempMeans[2])
# #plt.grid()
# #plt.show()


# # 4: Find sum of differences
# tempSumDiff = np.zeros(len(tempTraces[0]))
# for i in range(9):
#     for j in range(i):
#         tempSumDiff += np.abs(tempMeans[i] - tempMeans[j])

# plt.plot(tempSumDiff)
# plt.grid()
# plt.show()


# # 5: Find POIs
# POIs = []
# numPOIs = 5
# POIspacing = 5
# for i in range(numPOIs):
#     # Find the max
#     nextPOI = tempSumDiff.argmax()
#     POIs.append(nextPOI)
    
#     # Make sure we don't pick a nearby value
#     poiMin = max(0, nextPOI - POIspacing)
#     poiMax = min(nextPOI + POIspacing, len(tempSumDiff))
#     for j in range(poiMin, poiMax):
#         tempSumDiff[j] = 0
# # print (POIs)
# '''

# '''
# # 6: Fill up mean and covariance matrix for each HW
# meanMatrix = np.zeros((9, numPOIs))
# covMatrix  = np.zeros((9, numPOIs, numPOIs))
# for HW in range(9):
#     for i in range(numPOIs):
#         # Fill in mean
#         meanMatrix[HW][i] = tempMeans[HW][POIs[i]]
#         for j in range(numPOIs):
#             x = tempTracesHW[HW][:,POIs[i]]
#             y = tempTracesHW[HW][:,POIs[j]]
#             covMatrix[HW,i,j] = cov(x, y)
        
# #print meanMatrix
# #print covMatrix[0]


# # Template is ready!
# # 1: Load attack traces
# atkTraces = np.load("./test/traces.npy")
# atkPText  = np.load("./test/textin.npy")
# atkKey    = np.load("./test/keylist.npy")

# #print atkTraces
# #print atkPText
# print (atkKey)


# # 2: Attack
# # Running total of log P_k
# P_k = np.zeros(256)
# for j in range(len(atkTraces)):
#     # Grab key points and put them in a small matrix
#     a = [atkTraces[j][POIs[i]] for i in range(len(POIs))]#a是降维之后的曲线
    
#     # Test each key
#     for k in range(256):
#         # Find HW coming out of sbox
#         HW = hw[sbox[atkPText[j][3] ^ k]]
    
#         # Find p_{k,j}
#         rv = multivariate_normal(meanMatrix[HW], covMatrix[HW])
#         p_kj = rv.pdf(a)
   
#         # Add it to running total
#         P_k[k] += np.log(p_kj)

#     # Print our top 5 results so far
#     # Best match on the right
#     # for i in P_k:
#     #     print(hex(int(i)))
#     # print (P_k.argsort()[-5:])
#     print ([hex(int(x)) for x in P_k.argsort()[-5:]])

SCOPETYPE = 'OPENADC'
PLATFORM = 'CWLITEARM'
CRYPTO_TARGET = 'AVRCRYPTOLIB'
VERSION = 'HARDWARE'

from tqdm import tnrange
import numpy as np
    
final = []
def aes_internal(inputdata, key):
        return sbox[inputdata ^ key]
    # ###################
    # END SOLUTION
    # ###################
    

def calculate_diffs(guess, byteindex=0, bitnum=0):
    """Perform a simple DPA on two traces, uses global `textin_array` and `trace_array` """

    one_list = []
    zero_list = []

    for trace_index in range(numtraces):
        hypothetical_leakage = aes_internal(guess, textin_array[trace_index][byteindex])

        #Mask off the requested bit
        if hypothetical_leakage & (1<<bitnum):
            one_list.append(trace_array[trace_index])
        else:
            zero_list.append(trace_array[trace_index])

    one_avg = np.asarray(one_list).mean(axis=0)
    zero_avg = np.asarray(zero_list).mean(axis=0)
    return abs(one_avg - zero_avg)

for i in range(10000):
    
    N=i
    if VERSION == 'HARDWARE':
        %run "Lab 3_3 - DPA on Firmware Implementation of AES (HARDWARE).ipynb"
    elif VERSION == 'SIMULATED':
        %run "Lab 3_3 - DPA on Firmware Implementation of AES (SIMULATED).ipynb"

    # ###################
    # Add your code here
    # ###################
    #raise NotImplementedError("Add your code here, and delete this.")

    # ###################
    # START SOLUTION
    # ###################
    sbox = [
        # 0    1    2    3    4    5    6    7    8    9    a    b    c    d    e    f 
        0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76, # 0
        0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0, # 1
        0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15, # 2
        0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75, # 3
        0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84, # 4
        0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf, # 5
        0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8, # 6
        0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2, # 7
        0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73, # 8
        0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb, # 9
        0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79, # a
        0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08, # b
        0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a, # c
        0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e, # d
        0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf, # e
        0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16  # f
    ]

    




   
    numtraces = np.shape(trace_array)[0] #total number of traces
    numpoints = np.shape(trace_array)[1] #samples per trace
    #Store your key_guess here, compare to known_key
    key_guess = []
    known_key = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
    result = []
    for subkey in tnrange(0, 16, desc="Attacking Subkey"):
        # ###################
        # Add your code here
        # ###################
        #raise NotImplementedError("Add Your Code Here")

        # ###################
        # START SOLUTION
        # ###################
        max_diffs = [0]*256
        full_diffs = [0]*256
        for guess in range(0, 256):
            full_diff_trace = calculate_diffs(guess, subkey)
            max_diffs[guess] = np.max(full_diff_trace)
            full_diffs[guess] = full_diff_trace

        #Get argument sort, as each index is the actual key guess.
        sorted_args = np.argsort(max_diffs)[::-1]

        #Keep most likely
        key_guess.append(sorted_args[0])

        #Print results
        print("Subkey %2d - most likely %02X (actual %02X)"%(subkey, key_guess[subkey], known_key[subkey]))

        #Print other top guesses
        print(" Top 5 guesses: ")

        result.append(sorted_args[0])
        for i in range(0, 5):
            g = sorted_args[i]
            print("   %02X - Diff = %f"%(g, max_diffs[g]))


        print("\n")
        final.append(result)

        # ###################
        # END SOLUTION
        # ###################

corr = []
known_key = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
for i in range(len(final)):
    for j in range(len(known_key)):
        if final[i][j] == known_key[j]:
            num = num+1
    corr.append(num/16*100)
    
    
print (result)
print(known_key)