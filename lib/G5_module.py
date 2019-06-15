def bytes2hex(s):
    return "".join("{:02x}".format(c) for c in s)

def read_data(dstr):
    ## standard data style ##
    standard_head = "424d001c"
    data_len = 64

    index = dstr.find(standard_head)

    if(index == -1 or len(dstr) < 64):
        ## sense failed ##
        return (0, -1, -1, -1)

    else:
        ## pm2.5 data ##
        data_slice = dstr[index : index + data_len]
            
        ## cf_pm1 ##
        CFPM1_0 = (int(data_slice[8] + data_slice[9] + data_slice[10] + data_slice[11], 16))

        ## cf_pm2.5 ##
        CFPM2_5 = (int(data_slice[12] + data_slice[13] + data_slice[14] + data_slice[15], 16))

        ## cf_pm10 ##
        CFPM10 = (int(data_slice[16] + data_slice[17] + data_slice[18] + data_slice[19], 16))

        ## pm1 ##
        pm1 = (int(data_slice[20] + data_slice[21] + data_slice[22] + data_slice[23], 16))

        ## pm2.5 ##
        pm25 = (int(data_slice[24] + data_slice[25] + data_slice[26] + data_slice[27], 16))

        ## pm10 ##
        pm10 = (int(data_slice[28] + data_slice[29] + data_slice[30] + data_slice[31], 16))

    return (1, pm1, pm25, pm10)

