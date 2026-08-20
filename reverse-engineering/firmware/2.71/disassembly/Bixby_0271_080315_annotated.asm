; =============================================================================
; BIXBY 2.71 PIC16F877A - ANNOTATED REVERSE-ENGINEERING COPY
; Generated from the user-supplied gpdasm output. Original instructions unchanged.
;
; IMPORTANT: gpdasm register-name comments are not always bank-aware. Check
; STATUS.RP0/RP1 before trusting names for banked addresses.
;
; Confirmed protocol skeleton:
;   CRxx    = read register/status byte xx
;   CWxxYY  = write byte YY to command/register xx
;   Numeric fields are ASCII hexadecimal.
;   Responses are formatted in ASCII and terminated with LF (0x0A).
;
; Confirmed UART startup:
;   SPBRG = 0x20
;   TXSTA = 0x26
;   RCSTA = 0x90
; With a 20 MHz oscillator this is approximately 38.4 kbaud.
; =============================================================================


; The recognition of labels and registers is not always good, therefore
; be treated cautiously the results.

;===============================================================================
; DATA address definitions

Common_RAM      equ     0x0070                              ; size: 16 bytes

;===============================================================================
; CODE area

vector_reset:                                               ; address: 0x0000


; >>> RE NOTES @ 0x0000
; RESET VECTOR. PCLATH=0x18 then GOTO 0x1825, so real startup is at program address 0x1825.
; <<<
0000:  3018  movlw   0x18
0001:  008a  movwf   PCLATH                                 ; reg: 0x00a
0002:  2825  goto    label_004
0003:  0000  nop

vector_int:                                                 ; address: 0x0004


; >>> RE NOTES @ 0x0004
; INTERRUPT VECTOR. Saves W/STATUS/PCLATH/FSR and dispatches external, UART RX, and Timer2 sources.
; <<<
0004:  00ff  movwf   (Common_RAM + 15)                      ; reg: 0x07f
0005:  0e03  swapf   STATUS, W                              ; reg: 0x003
0006:  0183  clrf    STATUS                                 ; reg: 0x003
0007:  00a1  movwf   0x21                                   ; reg: 0x021
0008:  080a  movf    PCLATH, W                              ; reg: 0x00a
0009:  00a0  movwf   0x20                                   ; reg: 0x020
000a:  018a  clrf    PCLATH                                 ; reg: 0x00a
000b:  0804  movf    FSR, W                                 ; reg: 0x004
000c:  00a2  movwf   0x22                                   ; reg: 0x022
000d:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
000e:  00a3  movwf   0x23                                   ; reg: 0x023
000f:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0010:  00a4  movwf   0x24                                   ; reg: 0x024
0011:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0012:  00a5  movwf   0x25                                   ; reg: 0x025
0013:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
0014:  00a6  movwf   0x26                                   ; reg: 0x026
0015:  087b  movf    (Common_RAM + 11), W                   ; reg: 0x07b
0016:  00a7  movwf   0x27                                   ; reg: 0x027
0017:  1383  bcf     STATUS, IRP                            ; reg: 0x003, bit: 7
0018:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0019:  1e0b  btfss   INTCON, INTE                           ; reg: 0x00b, bit: 4
001a:  281d  goto    label_002
001b:  188b  btfsc   INTCON, INTF                           ; reg: 0x00b, bit: 1
001c:  283c  goto    label_006

label_002:                                                  ; address: 0x001d

001d:  308c  movlw   0x8c
001e:  0084  movwf   FSR                                    ; reg: 0x004
001f:  1e80  btfss   INDF, 0x5                              ; reg: 0x000
0020:  2823  goto    label_003
0021:  1a8c  btfsc   PIR1, RCIF                             ; reg: 0x00c, bit: 5
0022:  283f  goto    label_007

label_003:                                                  ; address: 0x0023

0023:  308c  movlw   0x8c
0024:  0084  movwf   FSR                                    ; reg: 0x004

label_004:                                                  ; address: 0x0025

0025:  1c80  btfss   INDF, 0x1                              ; reg: 0x000
0026:  2829  goto    label_005
0027:  188c  btfsc   PIR1, TMR2IF                           ; reg: 0x00c, bit: 1
0028:  2842  goto    label_008

label_005:                                                  ; address: 0x0029

0029:  0822  movf    0x22, W                                ; reg: 0x022
002a:  0084  movwf   FSR                                    ; reg: 0x004
002b:  0823  movf    0x23, W                                ; reg: 0x023
002c:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
002d:  0824  movf    0x24, W                                ; reg: 0x024
002e:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
002f:  0825  movf    0x25, W                                ; reg: 0x025
0030:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
0031:  0826  movf    0x26, W                                ; reg: 0x026
0032:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
0033:  0827  movf    0x27, W                                ; reg: 0x027
0034:  00fb  movwf   (Common_RAM + 11)                      ; reg: 0x07b
0035:  0820  movf    0x20, W                                ; reg: 0x020
0036:  008a  movwf   PCLATH                                 ; reg: 0x00a
0037:  0e21  swapf   0x21, W                                ; reg: 0x021
0038:  0083  movwf   STATUS                                 ; reg: 0x003
0039:  0eff  swapf   (Common_RAM + 15), F                   ; reg: 0x07f
003a:  0e7f  swapf   (Common_RAM + 15), W                   ; reg: 0x07f
003b:  0009  retfie

label_006:                                                  ; address: 0x003c

003c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
003d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
003e:  2947  goto    label_034

label_007:                                                  ; address: 0x003f

003f:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0040:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0041:  28ae  goto    label_009

label_008:                                                  ; address: 0x0042

0042:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0043:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0044:  298b  goto    label_043
0045:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
0046:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
0047:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
0048:  0782  addwf   PCL, F                                 ; reg: 0x002
0049:  3428  retlw   0x28
004a:  342d  retlw   0x2d
004b:  3432  retlw   0x32
004c:  3437  retlw   0x37
004d:  343c  retlw   0x3c
004e:  3441  retlw   0x41
004f:  3446  retlw   0x46
0050:  344b  retlw   0x4b
0051:  3450  retlw   0x50
0052:  3455  retlw   0x55
0053:  345a  retlw   0x5a

function_000:                                               ; address: 0x0054

0054:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
0055:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
0056:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
0057:  0782  addwf   PCL, F                                 ; reg: 0x002
0058:  3400  retlw   0x00
0059:  3400  retlw   0x00
005a:  3438  retlw   0x38
005b:  3404  retlw   0x04
005c:  3408  retlw   0x08
005d:  3407  retlw   0x07
005e:  348c  retlw   0x8c
005f:  340a  retlw   0x0a

function_001:                                               ; address: 0x0060

0060:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
0061:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
0062:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
0063:  0782  addwf   PCL, F                                 ; reg: 0x002
0064:  34a0  retlw   0xa0
0065:  3405  retlw   0x05
0066:  3440  retlw   0x40
0067:  340b  retlw   0x0b
0068:  3400  retlw   0x00
0069:  340f  retlw   0x0f
006a:  34e0  retlw   0xe0
006b:  3410  retlw   0x10
006c:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
006d:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
006e:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
006f:  0782  addwf   PCL, F                                 ; reg: 0x002
0070:  3464  retlw   0x64
0071:  3470  retlw   0x70
0072:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
0073:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
0074:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
0075:  0782  addwf   PCL, F                                 ; reg: 0x002
0076:  3400  retlw   0x00
0077:  3400  retlw   0x00
0078:  3408  retlw   0x08
0079:  3407  retlw   0x07

function_002:                                               ; address: 0x007a

007a:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
007b:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
007c:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
007d:  0782  addwf   PCL, F                                 ; reg: 0x002
007e:  3420  retlw   0x20
007f:  341c  retlw   0x1c
0080:  3480  retlw   0x80
0081:  3416  retlw   0x16
0082:  34c0  retlw   0xc0
0083:  3412  retlw   0x12
0084:  3412  retlw   0x12
0085:  3410  retlw   0x10
0086:  3410  retlw   0x10
0087:  340e  retlw   0x0e
0088:  3480  retlw   0x80
0089:  340c  retlw   0x0c
008a:  3440  retlw   0x40
008b:  340b  retlw   0x0b
008c:  343a  retlw   0x3a
008d:  340a  retlw   0x0a

function_003:                                               ; address: 0x008e

008e:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
008f:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
0090:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
0091:  0782  addwf   PCL, F                                 ; reg: 0x002
0092:  3400  retlw   0x00
0093:  3400  retlw   0x00
0094:  3468  retlw   0x68
0095:  3401  retlw   0x01
0096:  34d0  retlw   0xd0
0097:  3402  retlw   0x02

function_004:                                               ; address: 0x0098

0098:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
0099:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
009a:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
009b:  0782  addwf   PCL, F                                 ; reg: 0x002
009c:  3410  retlw   0x10
009d:  340e  retlw   0x0e
009e:  3480  retlw   0x80
009f:  340c  retlw   0x0c
00a0:  3410  retlw   0x10
00a1:  340e  retlw   0x0e

function_005:                                               ; address: 0x00a2

00a2:  100a  bcf     PCLATH, 0x0                            ; reg: 0x00a
00a3:  108a  bcf     PCLATH, 0x1                            ; reg: 0x00a
00a4:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
00a5:  0782  addwf   PCL, F                                 ; reg: 0x002
00a6:  343c  retlw   0x3c
00a7:  344b  retlw   0x4b
00a8:  345a  retlw   0x5a
00a9:  3469  retlw   0x69
00aa:  3478  retlw   0x78
00ab:  3487  retlw   0x87
00ac:  3496  retlw   0x96
00ad:  34a5  retlw   0xa5

label_009:                                                  ; address: 0x00ae


; >>> RE NOTES @ 0x00AE
; UART RECEIVE ISR path. Reads RCREG and appends bytes into a ~29-byte circular/linear command buffer starting at RAM address 0xA3. Byte 0x03 resets the receive counters.
; <<<
00ae:  1e8c  btfss   PIR1, RCIF                             ; reg: 0x00c, bit: 5
00af:  28ce  goto    label_012
00b0:  081a  movf    RCREG, W                               ; reg: 0x01a
00b1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
00b2:  00e5  movwf   0x65                                   ; reg: 0x065
00b3:  0865  movf    0x65, W                                ; reg: 0x065
00b4:  3c03  sublw   0x03
00b5:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
00b6:  28ba  goto    label_010
00b7:  01c1  clrf    0x41                                   ; reg: 0x041
00b8:  01c0  clrf    0x40                                   ; reg: 0x040
00b9:  28cc  goto    label_011

label_010:                                                  ; address: 0x00ba

00ba:  0841  movf    0x41, W                                ; reg: 0x041
00bb:  0ac1  incf    0x41, F                                ; reg: 0x041
00bc:  3ea3  addlw   0xa3
00bd:  0084  movwf   FSR                                    ; reg: 0x004
00be:  0865  movf    0x65, W                                ; reg: 0x065
00bf:  0080  movwf   INDF                                   ; reg: 0x000
00c0:  0ac0  incf    0x40, F                                ; reg: 0x040
00c1:  0841  movf    0x41, W                                ; reg: 0x041
00c2:  3c1c  sublw   0x1c
00c3:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
00c4:  28cc  goto    label_011
00c5:  01c1  clrf    0x41                                   ; reg: 0x041
00c6:  0840  movf    0x40, W                                ; reg: 0x040
00c7:  3c1c  sublw   0x1c
00c8:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
00c9:  28cc  goto    label_011
00ca:  01c1  clrf    0x41                                   ; reg: 0x041
00cb:  01c0  clrf    0x40                                   ; reg: 0x040

label_011:                                                  ; address: 0x00cc

00cc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
00cd:  28ae  goto    label_009

label_012:                                                  ; address: 0x00ce

00ce:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
00cf:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
00d0:  2829  goto    label_005

label_013:                                                  ; address: 0x00d1

00d1:  1cd2  btfss   0x52, 0x1                              ; reg: 0x052
00d2:  28d8  goto    label_014
00d3:  135d  bcf     0x5d, 0x6                              ; reg: 0x05d
00d4:  16dd  bsf     0x5d, 0x5                              ; reg: 0x05d
00d5:  15dd  bsf     0x5d, 0x3                              ; reg: 0x05d
00d6:  11b0  bcf     0x30, 0x3                              ; reg: 0x030
00d7:  290b  goto    label_023

label_014:                                                  ; address: 0x00d8

00d8:  1c52  btfss   0x52, 0x0                              ; reg: 0x052
00d9:  28e0  goto    label_015
00da:  16c3  bsf     0x43, 0x5                              ; reg: 0x043
00db:  12d0  bcf     0x50, 0x5                              ; reg: 0x050
00dc:  175d  bsf     0x5d, 0x6                              ; reg: 0x05d
00dd:  12dd  bcf     0x5d, 0x5                              ; reg: 0x05d
00de:  11dd  bcf     0x5d, 0x3                              ; reg: 0x05d
00df:  290b  goto    label_023

label_015:                                                  ; address: 0x00e0

00e0:  1952  btfsc   0x52, 0x2                              ; reg: 0x052
00e1:  28e4  goto    label_016
00e2:  1dd2  btfss   0x52, 0x3                              ; reg: 0x052
00e3:  290b  goto    label_023

label_016:                                                  ; address: 0x00e4

00e4:  1ad2  btfsc   0x52, 0x5                              ; reg: 0x052
00e5:  28ed  goto    label_018
00e6:  0b55  decfsz  0x55, W                                ; reg: 0x055
00e7:  28e9  goto    label_017
00e8:  28ed  goto    label_018

label_017:                                                  ; address: 0x00e9

00e9:  0855  movf    0x55, W                                ; reg: 0x055
00ea:  3c04  sublw   0x04
00eb:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
00ec:  28fc  goto    label_020

label_018:                                                  ; address: 0x00ed

00ed:  1d52  btfss   0x52, 0x2                              ; reg: 0x052
00ee:  28f5  goto    label_019
00ef:  085d  movf    0x5d, W                                ; reg: 0x05d
00f0:  3907  andlw   0x07
00f1:  3c06  sublw   0x06
00f2:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
00f3:  28f5  goto    label_019
00f4:  0add  incf    0x5d, F                                ; reg: 0x05d

label_019:                                                  ; address: 0x00f5

00f5:  1dd2  btfss   0x52, 0x3                              ; reg: 0x052
00f6:  28fc  goto    label_020
00f7:  085d  movf    0x5d, W                                ; reg: 0x05d
00f8:  3907  andlw   0x07
00f9:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
00fa:  28fc  goto    label_020
00fb:  03dd  decf    0x5d, F                                ; reg: 0x05d

label_020:                                                  ; address: 0x00fc

00fc:  0b55  decfsz  0x55, W                                ; reg: 0x055
00fd:  28ff  goto    label_021
00fe:  0ad5  incf    0x55, F                                ; reg: 0x055

label_021:                                                  ; address: 0x00ff

00ff:  0855  movf    0x55, W                                ; reg: 0x055
0100:  3c04  sublw   0x04
0101:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0102:  2905  goto    label_022
0103:  3002  movlw   0x02
0104:  00d5  movwf   0x55                                   ; reg: 0x055

label_022:                                                  ; address: 0x0105

0105:  084c  movf    0x4c, W                                ; reg: 0x04c
0106:  065d  xorwf   0x5d, W                                ; reg: 0x05d
0107:  3907  andlw   0x07
0108:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0109:  290b  goto    label_023
010a:  165d  bsf     0x5d, 0x4                              ; reg: 0x05d

label_023:                                                  ; address: 0x010b

010b:  1ad2  btfsc   0x52, 0x5                              ; reg: 0x052
010c:  290f  goto    label_024
010d:  1e52  btfss   0x52, 0x4                              ; reg: 0x052
010e:  2910  goto    label_025

label_024:                                                  ; address: 0x010f

010f:  01d2  clrf    0x52                                   ; reg: 0x052

label_025:                                                  ; address: 0x0110

0110:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0111:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0112:  2944  goto    label_033

label_026:                                                  ; address: 0x0113

0113:  1e52  btfss   0x52, 0x4                              ; reg: 0x052
0114:  2918  goto    label_027
0115:  1252  bcf     0x52, 0x4                              ; reg: 0x052
0116:  16d2  bsf     0x52, 0x5                              ; reg: 0x052
0117:  292c  goto    label_028

label_027:                                                  ; address: 0x0118

0118:  3004  movlw   0x04
0119:  0088  movwf   PORTD                                  ; reg: 0x008
011a:  1052  bcf     0x52, 0x0                              ; reg: 0x052
011b:  1d88  btfss   PORTD, RD3                             ; reg: 0x008, bit: 3
011c:  1452  bsf     0x52, 0x0                              ; reg: 0x052
011d:  3024  movlw   0x24
011e:  0088  movwf   PORTD                                  ; reg: 0x008
011f:  10d2  bcf     0x52, 0x1                              ; reg: 0x052
0120:  1d88  btfss   PORTD, RD3                             ; reg: 0x008, bit: 3
0121:  14d2  bsf     0x52, 0x1                              ; reg: 0x052
0122:  3044  movlw   0x44
0123:  0088  movwf   PORTD                                  ; reg: 0x008
0124:  1152  bcf     0x52, 0x2                              ; reg: 0x052
0125:  1d88  btfss   PORTD, RD3                             ; reg: 0x008, bit: 3
0126:  1552  bsf     0x52, 0x2                              ; reg: 0x052
0127:  3064  movlw   0x64
0128:  0088  movwf   PORTD                                  ; reg: 0x008
0129:  11d2  bcf     0x52, 0x3                              ; reg: 0x052
012a:  1d88  btfss   PORTD, RD3                             ; reg: 0x008, bit: 3
012b:  15d2  bsf     0x52, 0x3                              ; reg: 0x052

label_028:                                                  ; address: 0x012c

012c:  1dd1  btfss   0x51, 0x3                              ; reg: 0x051
012d:  2931  goto    label_029
012e:  0852  movf    0x52, W                                ; reg: 0x052
012f:  04d3  iorwf   0x53, F                                ; reg: 0x053
0130:  2944  goto    label_033

label_029:                                                  ; address: 0x0131

0131:  0853  movf    0x53, W                                ; reg: 0x053
0132:  0252  subwf   0x52, W                                ; reg: 0x052
0133:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0134:  2937  goto    label_030
0135:  0ad4  incf    0x54, F                                ; reg: 0x054
0136:  293b  goto    label_031

label_030:                                                  ; address: 0x0137

0137:  01d4  clrf    0x54                                   ; reg: 0x054
0138:  01d5  clrf    0x55                                   ; reg: 0x055
0139:  0852  movf    0x52, W                                ; reg: 0x052
013a:  00d3  movwf   0x53                                   ; reg: 0x053

label_031:                                                  ; address: 0x013b

013b:  1ed2  btfss   0x52, 0x5                              ; reg: 0x052
013c:  293f  goto    label_032
013d:  30fc  movlw   0xfc
013e:  00d4  movwf   0x54                                   ; reg: 0x054

label_032:                                                  ; address: 0x013f

013f:  0854  movf    0x54, W                                ; reg: 0x054
0140:  39fc  andlw   0xfc
0141:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0142:  2944  goto    label_033
0143:  28d1  goto    label_013

label_033:                                                  ; address: 0x0144

0144:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0145:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0146:  2948  goto    label_035

label_034:                                                  ; address: 0x0147

0147:  2913  goto    label_026

label_035:                                                  ; address: 0x0148

0148:  01b2  clrf    0x32                                   ; reg: 0x032
0149:  01b1  clrf    0x31                                   ; reg: 0x031
014a:  17cc  bsf     0x4c, 0x7                              ; reg: 0x04c
014b:  0871  movf    (Common_RAM + 1), W                    ; reg: 0x071
014c:  0472  iorwf   (Common_RAM + 2), W                    ; reg: 0x072
014d:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
014e:  2953  goto    label_036
014f:  0871  movf    (Common_RAM + 1), W                    ; reg: 0x071
0150:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0151:  03f2  decf    (Common_RAM + 2), F                    ; reg: 0x072
0152:  03f1  decf    (Common_RAM + 1), F                    ; reg: 0x071

label_036:                                                  ; address: 0x0153

0153:  3002  movlw   0x02
0154:  06b0  xorwf   0x30, F                                ; reg: 0x030
0155:  1c86  btfss   PORTB, RB1                             ; reg: 0x006, bit: 1
0156:  295a  goto    label_037
0157:  0ac6  incf    0x46, F                                ; reg: 0x046
0158:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0159:  0ac7  incf    0x47, F                                ; reg: 0x047

label_037:                                                  ; address: 0x015a

015a:  0191  clrf    TMR2                                   ; reg: 0x011
015b:  108c  bcf     PIR1, TMR2IF                           ; reg: 0x00c, bit: 1
015c:  0ab5  incf    0x35, F                                ; reg: 0x035
015d:  1eb5  btfss   0x35, 0x5                              ; reg: 0x035
015e:  2967  goto    label_038
015f:  3082  movlw   0x82
0160:  00b5  movwf   0x35                                   ; reg: 0x035
0161:  0801  movf    TMR0, W                                ; reg: 0x001
0162:  190b  btfsc   INTCON, T0IF                           ; reg: 0x00b, bit: 2
0163:  30ff  movlw   0xff
0164:  00b4  movwf   0x34                                   ; reg: 0x034
0165:  0181  clrf    TMR0                                   ; reg: 0x001
0166:  110b  bcf     INTCON, T0IF                           ; reg: 0x00b, bit: 2

label_038:                                                  ; address: 0x0167

0167:  1186  bcf     PORTB, RB3                             ; reg: 0x006, bit: 3
0168:  3000  movlw   0x00
0169:  18b0  btfsc   0x30, 0x1                              ; reg: 0x030
016a:  3001  movlw   0x01
016b:  3901  andlw   0x01
016c:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
016d:  2986  goto    label_041
016e:  0829  movf    0x29, W                                ; reg: 0x029
016f:  07aa  addwf   0x2a, F                                ; reg: 0x02a
0170:  082a  movf    0x2a, W                                ; reg: 0x02a
0171:  3c63  sublw   0x63
0172:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0173:  297d  goto    label_039
0174:  3064  movlw   0x64
0175:  02aa  subwf   0x2a, F                                ; reg: 0x02a
0176:  15d6  bsf     0x56, 0x3                              ; reg: 0x056
0177:  1687  bsf     PORTC, RC5                             ; reg: 0x007, bit: 5
0178:  3060  movlw   0x60
0179:  0088  movwf   PORTD                                  ; reg: 0x008
017a:  1508  bsf     PORTD, RD2                             ; reg: 0x008, bit: 2
017b:  12d1  bcf     0x51, 0x5                              ; reg: 0x051
017c:  2985  goto    label_040

label_039:                                                  ; address: 0x017d

017d:  1ed1  btfss   0x51, 0x5                              ; reg: 0x051
017e:  2985  goto    label_040
017f:  11d6  bcf     0x56, 0x3                              ; reg: 0x056
0180:  1287  bcf     PORTC, RC5                             ; reg: 0x007, bit: 5
0181:  3060  movlw   0x60
0182:  0088  movwf   PORTD                                  ; reg: 0x008
0183:  1508  bsf     PORTD, RD2                             ; reg: 0x008, bit: 2
0184:  12d1  bcf     0x51, 0x5                              ; reg: 0x051

label_040:                                                  ; address: 0x0185

0185:  2987  goto    label_042

label_041:                                                  ; address: 0x0186

0186:  16d1  bsf     0x51, 0x5                              ; reg: 0x051

label_042:                                                  ; address: 0x0187

0187:  108b  bcf     INTCON, INTF                           ; reg: 0x00b, bit: 1
0188:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0189:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
018a:  2829  goto    label_005

label_043:                                                  ; address: 0x018b

018b:  0fb1  incfsz  0x31, F                                ; reg: 0x031
018c:  298f  goto    label_044
018d:  0f32  incfsz  0x32, W                                ; reg: 0x032
018e:  00b2  movwf   0x32                                   ; reg: 0x032

label_044:                                                  ; address: 0x018f

018f:  1fcc  btfss   0x4c, 0x7                              ; reg: 0x04c
0190:  2995  goto    label_045
0191:  13cc  bcf     0x4c, 0x7                              ; reg: 0x04c
0192:  0837  movf    0x37, W                                ; reg: 0x037
0193:  00b8  movwf   0x38                                   ; reg: 0x038
0194:  299a  goto    label_046

label_045:                                                  ; address: 0x0195

0195:  08b8  movf    0x38, F                                ; reg: 0x038
0196:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0197:  0bb8  decfsz  0x38, F                                ; reg: 0x038
0198:  299a  goto    label_046
0199:  1586  bsf     PORTB, RB3                             ; reg: 0x006, bit: 3

label_046:                                                  ; address: 0x019a

019a:  108c  bcf     PIR1, TMR2IF                           ; reg: 0x00c, bit: 1
019b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
019c:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
019d:  2829  goto    label_005

function_006:                                               ; address: 0x019e

019e:  3001  movlw   0x01
019f:  00f4  movwf   (Common_RAM + 4)                       ; reg: 0x074
01a0:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6

label_047:                                                  ; address: 0x01a1

01a1:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
01a2:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
01a3:  29a1  goto    label_047
01a4:  301f  movlw   0x1f
01a5:  0588  andwf   PORTD, F                               ; reg: 0x008

label_048:                                                  ; address: 0x01a6

01a6:  08f4  movf    (Common_RAM + 4), F                    ; reg: 0x074
01a7:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
01a8:  29b6  goto    label_050
01a9:  1687  bsf     PORTC, RC5                             ; reg: 0x007, bit: 5
01aa:  0848  movf    0x48, W                                ; reg: 0x048
01ab:  0574  andwf   (Common_RAM + 4), W                    ; reg: 0x074
01ac:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
01ad:  29af  goto    label_049
01ae:  1287  bcf     PORTC, RC5                             ; reg: 0x007, bit: 5

label_049:                                                  ; address: 0x01af

01af:  1107  bcf     PORTC, RC2                             ; reg: 0x007, bit: 2
01b0:  1507  bsf     PORTC, RC2                             ; reg: 0x007, bit: 2
01b1:  3020  movlw   0x20
01b2:  0788  addwf   PORTD, F                               ; reg: 0x008
01b3:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
01b4:  0df4  rlf     (Common_RAM + 4), F                    ; reg: 0x074
01b5:  29a6  goto    label_048

label_050:                                                  ; address: 0x01b6

01b6:  30c0  movlw   0xc0
01b7:  048b  iorwf   INTCON, F                              ; reg: 0x00b
01b8:  3400  retlw   0x00

label_051:                                                  ; address: 0x01b9

01b9:  3007  movlw   0x07
01ba:  00ad  movwf   0x2d                                   ; reg: 0x02d
01bb:  0185  clrf    PORTA                                  ; reg: 0x005
01bc:  0186  clrf    PORTB                                  ; reg: 0x006
01bd:  0187  clrf    PORTC                                  ; reg: 0x007
01be:  3004  movlw   0x04
01bf:  0089  movwf   PORTE                                  ; reg: 0x009
01c0:  01c8  clrf    0x48                                   ; reg: 0x048
01c1:  219e  call    function_006
01c2:  01c9  clrf    0x49                                   ; reg: 0x049
01c3:  01bb  clrf    0x3b                                   ; reg: 0x03b
01c4:  01bc  clrf    0x3c                                   ; reg: 0x03c
01c5:  01d5  clrf    0x55                                   ; reg: 0x055
01c6:  01d4  clrf    0x54                                   ; reg: 0x054
01c7:  01cb  clrf    0x4b                                   ; reg: 0x04b
01c8:  01ca  clrf    0x4a                                   ; reg: 0x04a
01c9:  01dd  clrf    0x5d                                   ; reg: 0x05d
01ca:  01d3  clrf    0x53                                   ; reg: 0x053
01cb:  0853  movf    0x53, W                                ; reg: 0x053
01cc:  00d2  movwf   0x52                                   ; reg: 0x052
01cd:  01d1  clrf    0x51                                   ; reg: 0x051
01ce:  01d7  clrf    0x57                                   ; reg: 0x057
01cf:  01b0  clrf    0x30                                   ; reg: 0x030
01d0:  30dc  movlw   0xdc
01d1:  00da  movwf   0x5a                                   ; reg: 0x05a
01d2:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
01d3:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
01d4:  2a13  goto    label_058

function_007:                                               ; address: 0x01d5

01d5:  1186  bcf     PORTB, RB3                             ; reg: 0x006, bit: 3
01d6:  01b3  clrf    0x33                                   ; reg: 0x033
01d7:  01b8  clrf    0x38                                   ; reg: 0x038
01d8:  01b7  clrf    0x37                                   ; reg: 0x037
01d9:  01b5  clrf    0x35                                   ; reg: 0x035
01da:  01b4  clrf    0x34                                   ; reg: 0x034
01db:  3400  retlw   0x00

function_008:                                               ; address: 0x01dc

01dc:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6

label_052:                                                  ; address: 0x01dd

01dd:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
01de:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
01df:  29dd  goto    label_052
01e0:  301f  movlw   0x1f
01e1:  0588  andwf   PORTD, F                               ; reg: 0x008
01e2:  3001  movlw   0x01
01e3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
01e4:  00d4  movwf   0x54                                   ; reg: 0x054

label_053:                                                  ; address: 0x01e5

01e5:  08d4  movf    0x54, F                                ; reg: 0x054
01e6:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
01e7:  29fb  goto    label_055
01e8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
01e9:  1287  bcf     PORTC, RC5                             ; reg: 0x007, bit: 5
01ea:  0856  movf    0x56, W                                ; reg: 0x056
01eb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
01ec:  0554  andwf   0x54, W                                ; reg: 0x054
01ed:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
01ee:  29f2  goto    label_054
01ef:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
01f0:  1687  bsf     PORTC, RC5                             ; reg: 0x007, bit: 5
01f1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_054:                                                  ; address: 0x01f2

01f2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
01f3:  1108  bcf     PORTD, RD2                             ; reg: 0x008, bit: 2
01f4:  1508  bsf     PORTD, RD2                             ; reg: 0x008, bit: 2
01f5:  3020  movlw   0x20
01f6:  0788  addwf   PORTD, F                               ; reg: 0x008
01f7:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
01f8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
01f9:  0dd4  rlf     0x54, F                                ; reg: 0x054
01fa:  29e5  goto    label_053

label_055:                                                  ; address: 0x01fb

01fb:  30c0  movlw   0xc0
01fc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
01fd:  048b  iorwf   INTCON, F                              ; reg: 0x00b
01fe:  3400  retlw   0x00

label_056:                                                  ; address: 0x01ff

01ff:  30bf  movlw   0xbf
0200:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0201:  0081  movwf   TMR0                                   ; reg: 0x001
0202:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0203:  0181  clrf    TMR0                                   ; reg: 0x001
0204:  110b  bcf     INTCON, T0IF                           ; reg: 0x00b, bit: 2
0205:  303f  movlw   0x3f
0206:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0207:  0085  movwf   PORTA                                  ; reg: 0x005
0208:  30d1  movlw   0xd1
0209:  0086  movwf   PORTB                                  ; reg: 0x006
020a:  3080  movlw   0x80
020b:  0087  movwf   PORTC                                  ; reg: 0x007

label_057:                                                  ; address: 0x020c

020c:  301b  movlw   0x1b
020d:  0088  movwf   PORTD                                  ; reg: 0x008
020e:  1409  bsf     PORTE, RE0                             ; reg: 0x009, bit: 0
020f:  1489  bsf     PORTE, RE1                             ; reg: 0x009, bit: 1
0210:  1109  bcf     PORTE, RE2                             ; reg: 0x009, bit: 2
0211:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0212:  29b9  goto    label_051

label_058:                                                  ; address: 0x0213

0213:  21d5  call    function_007
0214:  3074  movlw   0x74
0215:  0095  movwf   CCPR1L                                 ; reg: 0x015
0216:  30c6  movlw   0xc6
0217:  0096  movwf   CCPR1H                                 ; reg: 0x016
0218:  300b  movlw   0x0b
0219:  0097  movwf   CCP1CON                                ; reg: 0x017
021a:  3031  movlw   0x31
021b:  0090  movwf   T1CON                                  ; reg: 0x010
021c:  018f  clrf    TMR1H                                  ; reg: 0x00f
021d:  018e  clrf    TMR1L                                  ; reg: 0x00e
021e:  3009  movlw   0x09
021f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0220:  009f  movwf   ADCON0                                 ; reg: 0x01f
0221:  3081  movlw   0x81
0222:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0223:  009f  movwf   ADCON0                                 ; reg: 0x01f
0224:  3000  movlw   0x00
0225:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0226:  3804  iorlw   0x04
0227:  0092  movwf   T2CON                                  ; reg: 0x012
0228:  3042  movlw   0x42
0229:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
022a:  0092  movwf   T2CON                                  ; reg: 0x012
022b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
022c:  160b  bsf     INTCON, INTE                           ; reg: 0x00b, bit: 4
022d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
022e:  148c  bsf     PIR1, TMR2IF                           ; reg: 0x00c, bit: 1
022f:  30c0  movlw   0xc0
0230:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0231:  048b  iorwf   INTCON, F                              ; reg: 0x00b
0232:  30d1  movlw   0xd1
0233:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0234:  0086  movwf   PORTB                                  ; reg: 0x006
0235:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0236:  01d6  clrf    0x56                                   ; reg: 0x056
0237:  21dc  call    function_008
0238:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0239:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
023a:  2a48  goto    label_061

label_059:                                                  ; address: 0x023b

023b:  081a  movf    RCREG, W                               ; reg: 0x01a
023c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
023d:  00a3  movwf   0x23                                   ; reg: 0x023
023e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
023f:  1218  bcf     RCSTA, CREN                            ; reg: 0x018, bit: 4
0240:  1618  bsf     RCSTA, CREN                            ; reg: 0x018, bit: 4
0241:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0242:  01a3  clrf    0x23                                   ; reg: 0x023
0243:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0244:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0245:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0246:  2a49  goto    label_062

label_060:                                                  ; address: 0x0247

0247:  29ff  goto    label_056

label_061:                                                  ; address: 0x0248

0248:  2a3b  goto    label_059

label_062:                                                  ; address: 0x0249

0249:  30dc  movlw   0xdc
024a:  00da  movwf   0x5a                                   ; reg: 0x05a
024b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
024c:  01c2  clrf    0x42                                   ; reg: 0x042
024d:  01a0  clrf    0x20                                   ; reg: 0x020
024e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
024f:  11d1  bcf     0x51, 0x3                              ; reg: 0x051
0250:  107e  bcf     (Common_RAM + 14), 0x0                 ; reg: 0x07e
0251:  01cd  clrf    0x4d                                   ; reg: 0x04d
0252:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0253:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
0254:  2843  goto    label_231

function_009:                                               ; address: 0x0255

0255:  01e1  clrf    0x61                                   ; reg: 0x061
0256:  01e2  clrf    0x62                                   ; reg: 0x062
0257:  01eb  clrf    0x6b                                   ; reg: 0x06b
0258:  01ed  clrf    0x6d                                   ; reg: 0x06d
0259:  01ee  clrf    0x6e                                   ; reg: 0x06e
025a:  30f0  movlw   0xf0
025b:  05fe  andwf   (Common_RAM + 14), F                   ; reg: 0x07e
025c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
025d:  01c8  clrf    0x48                                   ; reg: 0x048
025e:  0848  movf    0x48, W                                ; reg: 0x048
025f:  3c07  sublw   0x07
0260:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0261:  2a68  goto    label_294
0262:  3063  movlw   0x63
0263:  0748  addwf   0x48, W                                ; reg: 0x048
0264:  0084  movwf   FSR                                    ; reg: 0x004
0265:  0180  clrf    INDF                                   ; reg: 0x000
0266:  0ac8  incf    0x48, F                                ; reg: 0x048
0267:  2a5e  goto    label_292
0268:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0269:  3400  retlw   0x00

function_010:                                               ; address: 0x026a

026a:  16d6  bsf     0x56, 0x5                              ; reg: 0x056
026b:  21dc  call    function_063
026c:  3400  retlw   0x00

function_011:                                               ; address: 0x026d

026d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
026e:  08d3  movf    0x53, F                                ; reg: 0x053
026f:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0270:  2a7a  goto    0x027a
0271:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0272:  18ad  btfsc   0x2d, 0x1                              ; reg: 0x02d
0273:  2a76  goto    0x0276
0274:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0275:  2a7a  goto    0x027a
0276:  226a  call    0x026a
0277:  1407  bsf     PORTC, RC0                             ; reg: 0x007, bit: 0
0278:  2a7c  goto    0x027c
0279:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
027a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
027b:  1007  bcf     PORTC, RC0                             ; reg: 0x007, bit: 0
027c:  3400  retlw   0x00
027d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
027e:  08d3  movf    0x53, F                                ; reg: 0x053
027f:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0280:  2a8a  goto    0x028a
0281:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0282:  182d  btfsc   0x2d, 0x0                              ; reg: 0x02d
0283:  2a86  goto    0x0286
0284:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0285:  2a8a  goto    0x028a
0286:  226a  call    0x026a
0287:  1487  bsf     PORTC, RC1                             ; reg: 0x007, bit: 1
0288:  2a8c  goto    0x028c
0289:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
028a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
028b:  1087  bcf     PORTC, RC1                             ; reg: 0x007, bit: 1
028c:  3400  retlw   0x00

function_012:                                               ; address: 0x028d

028d:  13ad  bcf     0x2d, 0x7                              ; reg: 0x02d
028e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
028f:  01d3  clrf    0x53                                   ; reg: 0x053
0290:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0291:  226d  call    0x026d
0292:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0293:  01d3  clrf    0x53                                   ; reg: 0x053
0294:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0295:  227d  call    0x027d
0296:  3400  retlw   0x00
0297:  300f  movlw   0x0f
0298:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0299:  05d8  andwf   0x58, F                                ; reg: 0x058
029a:  0858  movf    0x58, W                                ; reg: 0x058
029b:  3c09  sublw   0x09
029c:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
029d:  2aa2  goto    0x02a2
029e:  3057  movlw   0x57
029f:  0758  addwf   0x58, W                                ; reg: 0x058
02a0:  00d9  movwf   0x59                                   ; reg: 0x059
02a1:  2aa5  goto    0x02a5
02a2:  3030  movlw   0x30
02a3:  0758  addwf   0x58, W                                ; reg: 0x058
02a4:  00d9  movwf   0x59                                   ; reg: 0x059
02a5:  0859  movf    0x59, W                                ; reg: 0x059
02a6:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
02a7:  1a0c  btfsc   PIR1, TXIF                             ; reg: 0x00c, bit: 4
02a8:  2aab  goto    0x02ab
02a9:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02aa:  2aa6  goto    0x02a6
02ab:  0099  movwf   TXREG                                  ; reg: 0x019
02ac:  3400  retlw   0x00

function_013:                                               ; address: 0x02ad

02ad:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02ae:  0e56  swapf   0x56, W                                ; reg: 0x056
02af:  00d7  movwf   0x57                                   ; reg: 0x057
02b0:  300f  movlw   0x0f
02b1:  05d7  andwf   0x57, F                                ; reg: 0x057
02b2:  0857  movf    0x57, W                                ; reg: 0x057
02b3:  00d8  movwf   0x58                                   ; reg: 0x058
02b4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
02b5:  2297  call    0x0297
02b6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02b7:  0856  movf    0x56, W                                ; reg: 0x056
02b8:  00d8  movwf   0x58                                   ; reg: 0x058
02b9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_063:                                                  ; address: 0x02ba

02ba:  2297  call    0x0297
02bb:  3400  retlw   0x00

function_014:                                               ; address: 0x02bc

02bc:  19d1  btfsc   0x51, 0x3                              ; reg: 0x051
02bd:  2ad4  goto    0x02d4
02be:  3044  movlw   0x44
02bf:  1e0c  btfss   PIR1, TXIF                             ; reg: 0x00c, bit: 4
02c0:  2abf  goto    0x02bf
02c1:  0099  movwf   TXREG                                  ; reg: 0x019
02c2:  3057  movlw   0x57
02c3:  1e0c  btfss   PIR1, TXIF                             ; reg: 0x00c, bit: 4
02c4:  2ac3  goto    0x02c3
02c5:  0099  movwf   TXREG                                  ; reg: 0x019
02c6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02c7:  0853  movf    0x53, W                                ; reg: 0x053
02c8:  00d6  movwf   0x56                                   ; reg: 0x056
02c9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
02ca:  22ad  call    0x02ad
02cb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02cc:  0854  movf    0x54, W                                ; reg: 0x054
02cd:  00d6  movwf   0x56                                   ; reg: 0x056
02ce:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
02cf:  22ad  call    0x02ad
02d0:  300a  movlw   0x0a
02d1:  1e0c  btfss   PIR1, TXIF                             ; reg: 0x00c, bit: 4
02d2:  2ad1  goto    0x02d1
02d3:  0099  movwf   TXREG                                  ; reg: 0x019
02d4:  3400  retlw   0x00
02d5:  1394  bcf     SSPCON, WCOL                           ; reg: 0x014, bit: 7
02d6:  118c  bcf     PIR1, SSPIF                            ; reg: 0x00c, bit: 3
02d7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02d8:  0855  movf    0x55, W                                ; reg: 0x055
02d9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
02da:  0093  movwf   SSPBUF                                 ; reg: 0x013
02db:  3002  movlw   0x02
02dc:  1b94  btfsc   SSPCON, WCOL                           ; reg: 0x014, bit: 7
02dd:  2ae5  goto    0x02e5
02de:  1d8c  btfss   PIR1, SSPIF                            ; reg: 0x00c, bit: 3
02df:  2ade  goto    0x02de
02e0:  3000  movlw   0x00
02e1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02e2:  1b11  btfsc   TMR2, 0x6                              ; reg: 0x011
02e3:  3001  movlw   0x01
02e4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
02e5:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
02e6:  3400  retlw   0x00
02e7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
02e8:  1591  bsf     TMR2, 0x3                              ; reg: 0x011
02e9:  1991  btfsc   TMR2, 0x3                              ; reg: 0x011
02ea:  2ae9  goto    0x02e9
02eb:  1877  btfsc   (Common_RAM + 7), 0x0                  ; reg: 0x077
02ec:  1291  bcf     TMR2, 0x5                              ; reg: 0x011
02ed:  1c77  btfss   (Common_RAM + 7), 0x0                  ; reg: 0x077
02ee:  1691  bsf     TMR2, 0x5                              ; reg: 0x011
02ef:  1611  bsf     TMR2, 0x4                              ; reg: 0x011
02f0:  1a11  btfsc   TMR2, 0x4                              ; reg: 0x011
02f1:  2af0  goto    0x02f0
02f2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
02f3:  0813  movf    SSPBUF, W                              ; reg: 0x013
02f4:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
02f5:  3400  retlw   0x00

function_015:                                               ; address: 0x02f6

02f6:  0d2c  rlf     0x2c, W                                ; reg: 0x02c
02f7:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
02f8:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
02f9:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
02fa:  30f8  movlw   0xf8
02fb:  05f7  andwf   (Common_RAM + 7), F                    ; reg: 0x077
02fc:  081f  movf    ADCON0, W                              ; reg: 0x01f
02fd:  39c7  andlw   0xc7
02fe:  0477  iorwf   (Common_RAM + 7), W                    ; reg: 0x077
02ff:  009f  movwf   ADCON0                                 ; reg: 0x01f
0300:  3053  movlw   0x53
0301:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0302:  0bf7  decfsz  (Common_RAM + 7), F                    ; reg: 0x077
0303:  2b02  goto    0x0302
0304:  08ac  movf    0x2c, F                                ; reg: 0x02c
0305:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0306:  2b07  goto    0x0307
0307:  0b2c  decfsz  0x2c, W                                ; reg: 0x02c
0308:  2b10  goto    0x0310
0309:  1886  btfsc   PORTB, RB1                             ; reg: 0x006, bit: 1
030a:  2b10  goto    0x0310
030b:  151f  bsf     ADCON0, GO                             ; reg: 0x01f, bit: 2
030c:  191f  btfsc   ADCON0, GO                             ; reg: 0x01f, bit: 2
030d:  2b0c  goto    0x030c
030e:  081e  movf    ADRESH, W                              ; reg: 0x01e
030f:  00d7  movwf   0x57                                   ; reg: 0x057
0310:  082c  movf    0x2c, W                                ; reg: 0x02c
0311:  3c02  sublw   0x02
0312:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0313:  2b3e  goto    0x033e
0314:  151f  bsf     ADCON0, GO                             ; reg: 0x01f, bit: 2
0315:  191f  btfsc   ADCON0, GO                             ; reg: 0x01f, bit: 2
0316:  2b15  goto    0x0315
0317:  081e  movf    ADRESH, W                              ; reg: 0x01e
0318:  00d8  movwf   0x58                                   ; reg: 0x058
0319:  0858  movf    0x58, W                                ; reg: 0x058
031a:  3c14  sublw   0x14
031b:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
031c:  2b29  goto    0x0329
031d:  1ad6  btfsc   0x56, 0x5                              ; reg: 0x056
031e:  2b21  goto    0x0321
031f:  0aef  incf    0x6f, F                                ; reg: 0x06f
0320:  2b26  goto    0x0326
0321:  086f  movf    0x6f, W                                ; reg: 0x06f
0322:  3c06  sublw   0x06
0323:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0324:  2b26  goto    0x0326
0325:  01ef  clrf    0x6f                                   ; reg: 0x06f
0326:  1bad  btfsc   0x2d, 0x7                              ; reg: 0x02d
0327:  2b29  goto    0x0329
0328:  0aef  incf    0x6f, F                                ; reg: 0x06f
0329:  086f  movf    0x6f, W                                ; reg: 0x06f
032a:  3c06  sublw   0x06
032b:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
032c:  2b3e  goto    0x033e
032d:  228d  call    0x028d
032e:  226a  call    0x026a
032f:  174f  bsf     0x4f, 0x6                              ; reg: 0x04f
0330:  144f  bsf     0x4f, 0x0                              ; reg: 0x04f
0331:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
0332:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
0333:  301c  movlw   0x1c
0334:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0335:  00d3  movwf   0x53                                   ; reg: 0x053
0336:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0337:  0858  movf    0x58, W                                ; reg: 0x058
0338:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0339:  00d4  movwf   0x54                                   ; reg: 0x054
033a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
033b:  22bc  call    0x02bc
033c:  300c  movlw   0x0c
033d:  00ef  movwf   0x6f                                   ; reg: 0x06f
033e:  082c  movf    0x2c, W                                ; reg: 0x02c
033f:  3c03  sublw   0x03
0340:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0341:  2b47  goto    0x0347
0342:  151f  bsf     ADCON0, GO                             ; reg: 0x01f, bit: 2
0343:  191f  btfsc   ADCON0, GO                             ; reg: 0x01f, bit: 2
0344:  2b43  goto    0x0343
0345:  081e  movf    ADRESH, W                              ; reg: 0x01e
0346:  00ae  movwf   0x2e                                   ; reg: 0x02e
0347:  082c  movf    0x2c, W                                ; reg: 0x02c
0348:  3c04  sublw   0x04
0349:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
034a:  2b50  goto    0x0350
034b:  151f  bsf     ADCON0, GO                             ; reg: 0x01f, bit: 2
034c:  191f  btfsc   ADCON0, GO                             ; reg: 0x01f, bit: 2
034d:  2b4c  goto    0x034c
034e:  081e  movf    ADRESH, W                              ; reg: 0x01e
034f:  00af  movwf   0x2f                                   ; reg: 0x02f
0350:  082c  movf    0x2c, W                                ; reg: 0x02c

label_064:                                                  ; address: 0x0351

0351:  3c05  sublw   0x05
0352:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0353:  2bb2  goto    0x03b2
0354:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0355:  0822  movf    0x22, W                                ; reg: 0x022
0356:  00d3  movwf   0x53                                   ; reg: 0x053
0357:  1411  bsf     TMR2, 0x0                              ; reg: 0x011
0358:  1811  btfsc   TMR2, 0x0                              ; reg: 0x011
0359:  2b58  goto    0x0358
035a:  309a  movlw   0x9a
035b:  00d5  movwf   0x55                                   ; reg: 0x055
035c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
035d:  22d5  call    0x02d5
035e:  3001  movlw   0x01
035f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0360:  00d5  movwf   0x55                                   ; reg: 0x055
0361:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0362:  22d5  call    0x02d5
0363:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0364:  1511  bsf     TMR2, 0x2                              ; reg: 0x011
0365:  1911  btfsc   TMR2, 0x2                              ; reg: 0x011
0366:  2b65  goto    0x0365
0367:  1411  bsf     TMR2, 0x0                              ; reg: 0x011
0368:  1811  btfsc   TMR2, 0x0                              ; reg: 0x011
0369:  2b68  goto    0x0368
036a:  309b  movlw   0x9b
036b:  00d5  movwf   0x55                                   ; reg: 0x055
036c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
036d:  22d5  call    0x02d5
036e:  3001  movlw   0x01
036f:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0370:  22e7  call    0x02e7
0371:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0372:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0373:  00d4  movwf   0x54                                   ; reg: 0x054
0374:  1511  bsf     TMR2, 0x2                              ; reg: 0x011
0375:  1911  btfsc   TMR2, 0x2                              ; reg: 0x011
0376:  2b75  goto    0x0375
0377:  0854  movf    0x54, W                                ; reg: 0x054
0378:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0379:  1f78  btfss   (Common_RAM + 8), 0x6                  ; reg: 0x078
037a:  2b57  goto    0x0357
037b:  1411  bsf     TMR2, 0x0                              ; reg: 0x011
037c:  1811  btfsc   TMR2, 0x0                              ; reg: 0x011
037d:  2b7c  goto    0x037c
037e:  309a  movlw   0x9a
037f:  00d5  movwf   0x55                                   ; reg: 0x055
0380:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0381:  22d5  call    0x02d5
0382:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0383:  01d5  clrf    0x55                                   ; reg: 0x055
0384:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0385:  22d5  call    0x02d5
0386:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0387:  1511  bsf     TMR2, 0x2                              ; reg: 0x011
0388:  1911  btfsc   TMR2, 0x2                              ; reg: 0x011
0389:  2b88  goto    0x0388
038a:  1411  bsf     TMR2, 0x0                              ; reg: 0x011
038b:  1811  btfsc   TMR2, 0x0                              ; reg: 0x011
038c:  2b8b  goto    0x038b
038d:  309b  movlw   0x9b
038e:  00d5  movwf   0x55                                   ; reg: 0x055
038f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0390:  22d5  call    0x02d5
0391:  3001  movlw   0x01
0392:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0393:  22e7  call    0x02e7
0394:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0395:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0396:  00a2  movwf   0x22                                   ; reg: 0x022
0397:  1511  bsf     TMR2, 0x2                              ; reg: 0x011
0398:  1911  btfsc   TMR2, 0x2                              ; reg: 0x011
0399:  2b98  goto    0x0398
039a:  3001  movlw   0x01
039b:  0753  addwf   0x53, W                                ; reg: 0x053
039c:  3a80  xorlw   0x80
039d:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
039e:  0822  movf    0x22, W                                ; reg: 0x022
039f:  3a80  xorlw   0x80
03a0:  0277  subwf   (Common_RAM + 7), W                    ; reg: 0x077
03a1:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
03a2:  2ba5  goto    0x03a5
03a3:  0aa2  incf    0x22, F                                ; reg: 0x022
03a4:  2bb1  goto    0x03b1
03a5:  3001  movlw   0x01
03a6:  0253  subwf   0x53, W                                ; reg: 0x053
03a7:  3a80  xorlw   0x80
03a8:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
03a9:  0822  movf    0x22, W                                ; reg: 0x022
03aa:  3a80  xorlw   0x80
03ab:  0277  subwf   (Common_RAM + 7), W                    ; reg: 0x077
03ac:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
03ad:  2bb1  goto    0x03b1
03ae:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
03af:  2bb1  goto    0x03b1
03b0:  03a2  decf    0x22, F                                ; reg: 0x022
03b1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
03b2:  0aac  incf    0x2c, F                                ; reg: 0x02c
03b3:  082c  movf    0x2c, W                                ; reg: 0x02c
03b4:  3c05  sublw   0x05
03b5:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
03b6:  2bb8  goto    0x03b8
03b7:  01ac  clrf    0x2c                                   ; reg: 0x02c
03b8:  3400  retlw   0x00

function_016:                                               ; address: 0x03b9

03b9:  3010  movlw   0x10
03ba:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
03bb:  00da  movwf   0x5a                                   ; reg: 0x05a
03bc:  01f7  clrf    (Common_RAM + 7)                       ; reg: 0x077
03bd:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
03be:  0cd7  rrf     0x57, F                                ; reg: 0x057
03bf:  0cd6  rrf     0x56, F                                ; reg: 0x056
03c0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
03c1:  2bc8  goto    0x03c8
03c2:  0858  movf    0x58, W                                ; reg: 0x058
03c3:  07f7  addwf   (Common_RAM + 7), F                    ; reg: 0x077
03c4:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
03c5:  0afa  incf    (Common_RAM + 10), F                   ; reg: 0x07a
03c6:  0859  movf    0x59, W                                ; reg: 0x059
03c7:  07fa  addwf   (Common_RAM + 10), F                   ; reg: 0x07a
03c8:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
03c9:  0cf7  rrf     (Common_RAM + 7), F                    ; reg: 0x077
03ca:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
03cb:  0cf8  rrf     (Common_RAM + 8), F                    ; reg: 0x078
03cc:  0bda  decfsz  0x5a, F                                ; reg: 0x05a
03cd:  2bbe  goto    0x03be
03ce:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
03cf:  3400  retlw   0x00

function_017:                                               ; address: 0x03d0

03d0:  1951  btfsc   0x51, 0x2                              ; reg: 0x051
03d1:  2bd6  goto    0x03d6
03d2:  3030  movlw   0x30
03d3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
03d4:  07da  addwf   0x5a, F                                ; reg: 0x05a
03d5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
03d6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
03d7:  085a  movf    0x5a, W                                ; reg: 0x05a
03d8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
03d9:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
03da:  008d  movwf   EEADR                                  ; reg: 0x10d
03db:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
03dc:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
03dd:  140c  bsf     EECON1, RD                             ; reg: 0x18c, bit: 0
03de:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
03df:  080c  movf    EEDATA, W                              ; reg: 0x10c
03e0:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
03e1:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
03e2:  00db  movwf   0x5b                                   ; reg: 0x0db
03e3:  085b  movf    0x5b, W                                ; reg: 0x0db
03e4:  00f8  movwf   0x78                                   ; reg: 0x0f8
03e5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
03e6:  3400  retlw   0x00

function_018:                                               ; address: 0x03e7

03e7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
03e8:  01e1  clrf    0x61                                   ; reg: 0x061
03e9:  01df  clrf    0x5f                                   ; reg: 0x05f
03ea:  01de  clrf    0x5e                                   ; reg: 0x05e
03eb:  3080  movlw   0x80
03ec:  00e0  movwf   0x60                                   ; reg: 0x060
03ed:  01e2  clrf    0x62                                   ; reg: 0x062
03ee:  0862  movf    0x62, W                                ; reg: 0x062
03ef:  3c07  sublw   0x07
03f0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
03f1:  2c1c  goto    0x041c
03f2:  085c  movf    0x5c, W                                ; reg: 0x05c
03f3:  0560  andwf   0x60, W                                ; reg: 0x060
03f4:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
03f5:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
03f6:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
03f7:  047a  iorwf   (Common_RAM + 10), W                   ; reg: 0x07a
03f8:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
03f9:  2c00  goto    0x0400
03fa:  085a  movf    0x5a, W                                ; reg: 0x05a
03fb:  07de  addwf   0x5e, F                                ; reg: 0x05e
03fc:  085b  movf    0x5b, W                                ; reg: 0x05b
03fd:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
03fe:  0f5b  incfsz  0x5b, W                                ; reg: 0x05b
03ff:  07df  addwf   0x5f, F                                ; reg: 0x05f
0400:  085a  movf    0x5a, W                                ; reg: 0x05a
0401:  3901  andlw   0x01
0402:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0403:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
0404:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
0405:  047a  iorwf   (Common_RAM + 10), W                   ; reg: 0x07a
0406:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0407:  2c0c  goto    0x040c
0408:  0860  movf    0x60, W                                ; reg: 0x060
0409:  07e1  addwf   0x61, F                                ; reg: 0x061
040a:  0860  movf    0x60, W                                ; reg: 0x060
040b:  07e1  addwf   0x61, F                                ; reg: 0x061
040c:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
040d:  0cdb  rrf     0x5b, F                                ; reg: 0x05b
040e:  0cda  rrf     0x5a, F                                ; reg: 0x05a
040f:  0861  movf    0x61, W                                ; reg: 0x061
0410:  3c80  sublw   0x80
0411:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0412:  2c18  goto    0x0418
0413:  3080  movlw   0x80
0414:  02e1  subwf   0x61, F                                ; reg: 0x061
0415:  0ada  incf    0x5a, F                                ; reg: 0x05a
0416:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0417:  0adb  incf    0x5b, F                                ; reg: 0x05b
0418:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0419:  0ce0  rrf     0x60, F                                ; reg: 0x060
041a:  0ae2  incf    0x62, F                                ; reg: 0x062
041b:  2bee  goto    0x03ee
041c:  085e  movf    0x5e, W                                ; reg: 0x05e
041d:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
041e:  085f  movf    0x5f, W                                ; reg: 0x05f
041f:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
0420:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0421:  3400  retlw   0x00

function_019:                                               ; address: 0x0422

0422:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0423:  01d9  clrf    0x59                                   ; reg: 0x059
0424:  1c7e  btfss   (Common_RAM + 14), 0x0                 ; reg: 0x07e
0425:  2c70  goto    0x0470
0426:  0855  movf    0x55, W                                ; reg: 0x055
0427:  00da  movwf   0x5a                                   ; reg: 0x05a
0428:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0429:  23d0  call    0x03d0
042a:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
042b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
042c:  00d8  movwf   0x58                                   ; reg: 0x058
042d:  0854  movf    0x54, W                                ; reg: 0x054
042e:  3c07  sublw   0x07
042f:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0430:  2c36  goto    0x0436
0431:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0432:  0cd4  rrf     0x54, F                                ; reg: 0x054
0433:  0cd3  rrf     0x53, F                                ; reg: 0x053
0434:  0ad9  incf    0x59, F                                ; reg: 0x059
0435:  2c2d  goto    0x042d
0436:  0854  movf    0x54, W                                ; reg: 0x054
0437:  00db  movwf   0x5b                                   ; reg: 0x05b
0438:  0853  movf    0x53, W                                ; reg: 0x053
0439:  00da  movwf   0x5a                                   ; reg: 0x05a
043a:  01dd  clrf    0x5d                                   ; reg: 0x05d
043b:  0858  movf    0x58, W                                ; reg: 0x058
043c:  00dc  movwf   0x5c                                   ; reg: 0x05c
043d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
043e:  23e7  call    0x03e7
043f:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0440:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0441:  00d7  movwf   0x57                                   ; reg: 0x057
0442:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0443:  00d6  movwf   0x56                                   ; reg: 0x056
0444:  0857  movf    0x57, W                                ; reg: 0x057
0445:  3c05  sublw   0x05
0446:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0447:  2c54  goto    0x0454
0448:  3aff  xorlw   0xff
0449:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
044a:  2c4f  goto    0x044f
044b:  0856  movf    0x56, W                                ; reg: 0x056
044c:  3c3d  sublw   0x3d
044d:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
044e:  2c54  goto    0x0454
044f:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0450:  0cd7  rrf     0x57, F                                ; reg: 0x057
0451:  0cd6  rrf     0x56, F                                ; reg: 0x056
0452:  0ad9  incf    0x59, F                                ; reg: 0x059
0453:  2c44  goto    0x0444
0454:  0857  movf    0x57, W                                ; reg: 0x057
0455:  00db  movwf   0x5b                                   ; reg: 0x05b
0456:  0856  movf    0x56, W                                ; reg: 0x056
0457:  00da  movwf   0x5a                                   ; reg: 0x05a
0458:  01dd  clrf    0x5d                                   ; reg: 0x05d
0459:  30a4  movlw   0xa4
045a:  00dc  movwf   0x5c                                   ; reg: 0x05c
045b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
045c:  23e7  call    0x03e7
045d:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
045e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
045f:  00d7  movwf   0x57                                   ; reg: 0x057
0460:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0461:  00d6  movwf   0x56                                   ; reg: 0x056
0462:  08d9  movf    0x59, F                                ; reg: 0x059
0463:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0464:  2c6a  goto    0x046a
0465:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0466:  0dd6  rlf     0x56, F                                ; reg: 0x056
0467:  0dd7  rlf     0x57, F                                ; reg: 0x057
0468:  03d9  decf    0x59, F                                ; reg: 0x059
0469:  2c62  goto    0x0462
046a:  0856  movf    0x56, W                                ; reg: 0x056
046b:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
046c:  0857  movf    0x57, W                                ; reg: 0x057
046d:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
046e:  2c75  goto    0x0475
046f:  2c75  goto    0x0475
0470:  0853  movf    0x53, W                                ; reg: 0x053
0471:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0472:  0854  movf    0x54, W                                ; reg: 0x054
0473:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
0474:  2c75  goto    0x0475
0475:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0476:  3400  retlw   0x00

function_020:                                               ; address: 0x0477

0477:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0478:  084e  movf    0x4e, W                                ; reg: 0x04e
0479:  00d7  movwf   0x57                                   ; reg: 0x057
047a:  084d  movf    0x4d, W                                ; reg: 0x04d
047b:  00d6  movwf   0x56                                   ; reg: 0x056
047c:  01d9  clrf    0x59                                   ; reg: 0x059
047d:  3018  movlw   0x18
047e:  00d8  movwf   0x58                                   ; reg: 0x058
047f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0480:  23b9  call    0x03b9
0481:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0482:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0483:  00ce  movwf   0x4e                                   ; reg: 0x04e
0484:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0485:  00cd  movwf   0x4d                                   ; reg: 0x04d
0486:  1c7e  btfss   (Common_RAM + 14), 0x0                 ; reg: 0x07e
0487:  2c9b  goto    0x049b
0488:  084e  movf    0x4e, W                                ; reg: 0x04e
0489:  00d4  movwf   0x54                                   ; reg: 0x054
048a:  084d  movf    0x4d, W                                ; reg: 0x04d
048b:  00d3  movwf   0x53                                   ; reg: 0x053
048c:  084f  movf    0x4f, W                                ; reg: 0x04f
048d:  00d5  movwf   0x55                                   ; reg: 0x055
048e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
048f:  2422  call    0x0422
0490:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0491:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0492:  00d1  movwf   0x51                                   ; reg: 0x051
0493:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0494:  00d0  movwf   0x50                                   ; reg: 0x050
0495:  0850  movf    0x50, W                                ; reg: 0x050
0496:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0497:  0851  movf    0x51, W                                ; reg: 0x051
0498:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
0499:  2ca0  goto    0x04a0
049a:  2ca0  goto    0x04a0
049b:  084d  movf    0x4d, W                                ; reg: 0x04d
049c:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
049d:  084e  movf    0x4e, W                                ; reg: 0x04e
049e:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
049f:  2ca0  goto    0x04a0
04a0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
04a1:  3400  retlw   0x00
04a2:  01f8  clrf    (Common_RAM + 8)                       ; reg: 0x078
04a3:  01f9  clrf    (Common_RAM + 9)                       ; reg: 0x079
04a4:  01f7  clrf    (Common_RAM + 7)                       ; reg: 0x077
04a5:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
04a6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
04a7:  0857  movf    0x57, W                                ; reg: 0x057
04a8:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
04a9:  2cad  goto    0x04ad
04aa:  0856  movf    0x56, W                                ; reg: 0x056
04ab:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
04ac:  2cc7  goto    0x04c7
04ad:  3010  movlw   0x10
04ae:  00d8  movwf   0x58                                   ; reg: 0x058
04af:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
04b0:  0dd4  rlf     0x54, F                                ; reg: 0x054
04b1:  0dd5  rlf     0x55, F                                ; reg: 0x055
04b2:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
04b3:  0dfa  rlf     (Common_RAM + 10), F                   ; reg: 0x07a
04b4:  0857  movf    0x57, W                                ; reg: 0x057
04b5:  027a  subwf   (Common_RAM + 10), W                   ; reg: 0x07a
04b6:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
04b7:  2cba  goto    0x04ba
04b8:  0856  movf    0x56, W                                ; reg: 0x056
04b9:  0277  subwf   (Common_RAM + 7), W                    ; reg: 0x077
04ba:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
04bb:  2cc3  goto    0x04c3
04bc:  0856  movf    0x56, W                                ; reg: 0x056
04bd:  02f7  subwf   (Common_RAM + 7), F                    ; reg: 0x077
04be:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
04bf:  03fa  decf    (Common_RAM + 10), F                   ; reg: 0x07a
04c0:  0857  movf    0x57, W                                ; reg: 0x057
04c1:  02fa  subwf   (Common_RAM + 10), F                   ; reg: 0x07a
04c2:  1403  bsf     STATUS, C                              ; reg: 0x003, bit: 0
04c3:  0df8  rlf     (Common_RAM + 8), F                    ; reg: 0x078
04c4:  0df9  rlf     (Common_RAM + 9), F                    ; reg: 0x079
04c5:  0bd8  decfsz  0x58, F                                ; reg: 0x058
04c6:  2caf  goto    0x04af
04c7:  0000  nop
04c8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
04c9:  3400  retlw   0x00
04ca:  1c88  btfss   PORTD, RD1                             ; reg: 0x008, bit: 1
04cb:  2cec  goto    0x04ec
04cc:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
04cd:  0853  movf    0x53, W                                ; reg: 0x053
04ce:  3c05  sublw   0x05
04cf:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
04d0:  2cd4  goto    0x04d4
04d1:  3006  movlw   0x06
04d2:  00d3  movwf   0x53                                   ; reg: 0x053
04d3:  01d2  clrf    0x52                                   ; reg: 0x052
04d4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
04d5:  084c  movf    0x4c, W                                ; reg: 0x04c
04d6:  3970  andlw   0x70
04d7:  3c2f  sublw   0x2f
04d8:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
04d9:  2cec  goto    0x04ec
04da:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
04db:  0c53  rrf     0x53, W                                ; reg: 0x053
04dc:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
04dd:  0c52  rrf     0x52, W                                ; reg: 0x052
04de:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
04df:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
04e0:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
04e1:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
04e2:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
04e3:  301f  movlw   0x1f
04e4:  05fa  andwf   (Common_RAM + 10), F                   ; reg: 0x07a
04e5:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
04e6:  07d2  addwf   0x52, F                                ; reg: 0x052
04e7:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
04e8:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
04e9:  0f7a  incfsz  (Common_RAM + 10), W                   ; reg: 0x07a
04ea:  07d3  addwf   0x53, F                                ; reg: 0x053
04eb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
04ec:  1e08  btfss   PORTD, RD4                             ; reg: 0x008, bit: 4
04ed:  2d04  goto    0x0504
04ee:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
04ef:  0852  movf    0x52, W                                ; reg: 0x052
04f0:  0453  iorwf   0x53, W                                ; reg: 0x053
04f1:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
04f2:  2d03  goto    0x0503
04f3:  0c53  rrf     0x53, W                                ; reg: 0x053
04f4:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
04f5:  0c52  rrf     0x52, W                                ; reg: 0x052
04f6:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
04f7:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
04f8:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
04f9:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
04fa:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
04fb:  301f  movlw   0x1f
04fc:  05fa  andwf   (Common_RAM + 10), F                   ; reg: 0x07a
04fd:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
04fe:  07d2  addwf   0x52, F                                ; reg: 0x052
04ff:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
0500:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0501:  0f7a  incfsz  (Common_RAM + 10), W                   ; reg: 0x07a
0502:  07d3  addwf   0x53, F                                ; reg: 0x053
0503:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0504:  1e50  btfss   0x50, 0x4                              ; reg: 0x050
0505:  2d1d  goto    0x051d
0506:  306c  movlw   0x6c
0507:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0508:  00da  movwf   0x5a                                   ; reg: 0x05a
0509:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
050a:  23d0  call    0x03d0
050b:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
050c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
050d:  00d4  movwf   0x54                                   ; reg: 0x054
050e:  0853  movf    0x53, W                                ; reg: 0x053
050f:  00db  movwf   0x5b                                   ; reg: 0x05b
0510:  0852  movf    0x52, W                                ; reg: 0x052
0511:  00da  movwf   0x5a                                   ; reg: 0x05a
0512:  01dd  clrf    0x5d                                   ; reg: 0x05d
0513:  0854  movf    0x54, W                                ; reg: 0x054
0514:  00dc  movwf   0x5c                                   ; reg: 0x05c
0515:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0516:  23e7  call    0x03e7
0517:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0518:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0519:  00d3  movwf   0x53                                   ; reg: 0x053
051a:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
051b:  00d2  movwf   0x52                                   ; reg: 0x052
051c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
051d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
051e:  0853  movf    0x53, W                                ; reg: 0x053
051f:  00d5  movwf   0x55                                   ; reg: 0x055
0520:  0852  movf    0x52, W                                ; reg: 0x052
0521:  00d4  movwf   0x54                                   ; reg: 0x054
0522:  01d7  clrf    0x57                                   ; reg: 0x057
0523:  3018  movlw   0x18
0524:  00d6  movwf   0x56                                   ; reg: 0x056
0525:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0526:  24a2  call    0x04a2
0527:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0528:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0529:  00d3  movwf   0x53                                   ; reg: 0x053
052a:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
052b:  00d2  movwf   0x52                                   ; reg: 0x052
052c:  0853  movf    0x53, W                                ; reg: 0x053
052d:  3c00  sublw   0x00
052e:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
052f:  2d33  goto    0x0533
0530:  01d3  clrf    0x53                                   ; reg: 0x053
0531:  30ff  movlw   0xff
0532:  00d2  movwf   0x52                                   ; reg: 0x052
0533:  0852  movf    0x52, W                                ; reg: 0x052
0534:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0535:  0233  subwf   0x33, W                                ; reg: 0x033
0536:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0537:  2d3d  goto    0x053d
0538:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0539:  08d3  movf    0x53, F                                ; reg: 0x053
053a:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
053b:  2d44  goto    0x0544
053c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
053d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
053e:  0852  movf    0x52, W                                ; reg: 0x052
053f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0540:  00b3  movwf   0x33                                   ; reg: 0x033
0541:  30ff  movlw   0xff
0542:  00bc  movwf   0x3c                                   ; reg: 0x03c
0543:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0544:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0545:  3400  retlw   0x00

function_021:                                               ; address: 0x0546

0546:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0547:  084f  movf    0x4f, W                                ; reg: 0x04f
0548:  00db  movwf   0x5b                                   ; reg: 0x05b
0549:  084e  movf    0x4e, W                                ; reg: 0x04e
054a:  00da  movwf   0x5a                                   ; reg: 0x05a
054b:  01dd  clrf    0x5d                                   ; reg: 0x05d
054c:  3026  movlw   0x26
054d:  00dc  movwf   0x5c                                   ; reg: 0x05c
054e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
054f:  23e7  call    0x03e7
0550:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0551:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0552:  00d1  movwf   0x51                                   ; reg: 0x051
0553:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0554:  00d0  movwf   0x50                                   ; reg: 0x050
0555:  0851  movf    0x51, W                                ; reg: 0x051
0556:  00db  movwf   0x5b                                   ; reg: 0x05b
0557:  0850  movf    0x50, W                                ; reg: 0x050
0558:  00da  movwf   0x5a                                   ; reg: 0x05a
0559:  01dd  clrf    0x5d                                   ; reg: 0x05d
055a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
055b:  082e  movf    0x2e, W                                ; reg: 0x02e
055c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
055d:  00dc  movwf   0x5c                                   ; reg: 0x05c
055e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
055f:  23e7  call    0x03e7
0560:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0561:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0562:  00d1  movwf   0x51                                   ; reg: 0x051
0563:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0564:  00d0  movwf   0x50                                   ; reg: 0x050
0565:  084f  movf    0x4f, W                                ; reg: 0x04f
0566:  00db  movwf   0x5b                                   ; reg: 0x05b
0567:  084e  movf    0x4e, W                                ; reg: 0x04e
0568:  00da  movwf   0x5a                                   ; reg: 0x05a
0569:  01dd  clrf    0x5d                                   ; reg: 0x05d
056a:  3059  movlw   0x59
056b:  00dc  movwf   0x5c                                   ; reg: 0x05c
056c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
056d:  23e7  call    0x03e7
056e:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
056f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0570:  07d0  addwf   0x50, F                                ; reg: 0x050
0571:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0572:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0573:  0f79  incfsz  (Common_RAM + 9), W                    ; reg: 0x079
0574:  07d1  addwf   0x51, F                                ; reg: 0x051
0575:  0851  movf    0x51, W                                ; reg: 0x051
0576:  00d3  movwf   0x53                                   ; reg: 0x053
0577:  0850  movf    0x50, W                                ; reg: 0x050
0578:  00d2  movwf   0x52                                   ; reg: 0x052
0579:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
057a:  24ca  call    0x04ca
057b:  3400  retlw   0x00

function_022:                                               ; address: 0x057c

057c:  084c  movf    0x4c, W                                ; reg: 0x04c
057d:  3970  andlw   0x70
057e:  3c30  sublw   0x30
057f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0580:  2d86  goto    0x0586
0581:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0582:  08c9  movf    0x49, F                                ; reg: 0x049
0583:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0584:  2da5  goto    0x05a5
0585:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0586:  084c  movf    0x4c, W                                ; reg: 0x04c
0587:  3907  andlw   0x07
0588:  20a2  call    0x00a2
0589:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
058a:  00cb  movwf   0x4b                                   ; reg: 0x04b
058b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
058c:  084c  movf    0x4c, W                                ; reg: 0x04c
058d:  3907  andlw   0x07
058e:  3e40  addlw   0x40
058f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0590:  00cc  movwf   0x4c                                   ; reg: 0x04c
0591:  01ce  clrf    0x4e                                   ; reg: 0x04e
0592:  084b  movf    0x4b, W                                ; reg: 0x04b
0593:  00cd  movwf   0x4d                                   ; reg: 0x04d
0594:  084c  movf    0x4c, W                                ; reg: 0x04c
0595:  00cf  movwf   0x4f                                   ; reg: 0x04f
0596:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0597:  2477  call    0x0477
0598:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0599:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
059a:  00cd  movwf   0x4d                                   ; reg: 0x04d
059b:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
059c:  00cc  movwf   0x4c                                   ; reg: 0x04c
059d:  084d  movf    0x4d, W                                ; reg: 0x04d
059e:  00cf  movwf   0x4f                                   ; reg: 0x04f
059f:  084c  movf    0x4c, W                                ; reg: 0x04c
05a0:  00ce  movwf   0x4e                                   ; reg: 0x04e
05a1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05a2:  2546  call    0x0546
05a3:  2db0  goto    0x05b0
05a4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05a5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05a6:  084c  movf    0x4c, W                                ; reg: 0x04c
05a7:  3970  andlw   0x70
05a8:  3c20  sublw   0x20
05a9:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
05aa:  2db0  goto    0x05b0
05ab:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05ac:  01d3  clrf    0x53                                   ; reg: 0x053
05ad:  01d2  clrf    0x52                                   ; reg: 0x052
05ae:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05af:  24ca  call    0x04ca
05b0:  3400  retlw   0x00

function_023:                                               ; address: 0x05b1

05b1:  19d1  btfsc   0x51, 0x3                              ; reg: 0x051
05b2:  2dcb  goto    0x05cb
05b3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05b4:  01c9  clrf    0x49                                   ; reg: 0x049
05b5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05b6:  257c  call    0x057c
05b7:  0857  movf    0x57, W                                ; reg: 0x057
05b8:  3c13  sublw   0x13
05b9:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
05ba:  2dc0  goto    0x05c0
05bb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05bc:  08c8  movf    0x48, F                                ; reg: 0x048
05bd:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
05be:  2dc9  goto    0x05c9
05bf:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05c0:  3008  movlw   0x08
05c1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05c2:  00d3  movwf   0x53                                   ; reg: 0x053
05c3:  3034  movlw   0x34
05c4:  00d2  movwf   0x52                                   ; reg: 0x052
05c5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05c6:  24ca  call    0x04ca
05c7:  2dcb  goto    0x05cb
05c8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05c9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05ca:  21d5  call    0x01d5
05cb:  3400  retlw   0x00

function_024:                                               ; address: 0x05cc

05cc:  30ce  movlw   0xce
05cd:  0084  movwf   FSR                                    ; reg: 0x004
05ce:  0800  movf    INDF, W                                ; reg: 0x000
05cf:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
05d0:  2de0  goto    0x05e0
05d1:  3003  movlw   0x03
05d2:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
05d3:  01f7  clrf    (Common_RAM + 7)                       ; reg: 0x077
05d4:  0bf7  decfsz  (Common_RAM + 7), F                    ; reg: 0x077
05d5:  2dd4  goto    0x05d4
05d6:  0bf8  decfsz  (Common_RAM + 8), F                    ; reg: 0x078
05d7:  2dd3  goto    0x05d3
05d8:  303c  movlw   0x3c
05d9:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
05da:  0bf7  decfsz  (Common_RAM + 7), F                    ; reg: 0x077
05db:  2dda  goto    0x05da
05dc:  0000  nop
05dd:  0000  nop
05de:  0b80  decfsz  INDF, F                                ; reg: 0x000
05df:  2dd1  goto    0x05d1
05e0:  3400  retlw   0x00

label_065:                                                  ; address: 0x05e1

05e1:  3001  movlw   0x01
05e2:  00c8  movwf   0x48                                   ; reg: 0x048
05e3:  219e  call    0x019e
05e4:  300a  movlw   0x0a
05e5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05e6:  00ce  movwf   0x4e                                   ; reg: 0x04e
05e7:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05e8:  25cc  call    0x05cc
05e9:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
05ea:  0dc8  rlf     0x48, F                                ; reg: 0x048
05eb:  08c8  movf    0x48, F                                ; reg: 0x048
05ec:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
05ed:  2def  goto    0x05ef
05ee:  2de3  goto    0x05e3
05ef:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
05f0:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
05f1:  2e05  goto    label_069

label_066:                                                  ; address: 0x05f2

05f2:  3080  movlw   0x80
05f3:  00c8  movwf   0x48                                   ; reg: 0x048

label_067:                                                  ; address: 0x05f4

05f4:  219e  call    function_006
05f5:  300a  movlw   0x0a
05f6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
05f7:  00ce  movwf   0x4e                                   ; reg: 0x04e
05f8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
05f9:  25cc  call    function_024
05fa:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
05fb:  0cc8  rrf     0x48, F                                ; reg: 0x048
05fc:  08c8  movf    0x48, F                                ; reg: 0x048
05fd:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
05fe:  2e00  goto    label_068
05ff:  2df4  goto    label_067

label_068:                                                  ; address: 0x0600

0600:  219e  call    function_006
0601:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0602:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0603:  2e16  goto    label_071

function_025:                                               ; address: 0x0604

0604:  2de1  goto    label_065

label_069:                                                  ; address: 0x0605

0605:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0606:  0848  movf    0x48, W                                ; reg: 0x048
0607:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0608:  00c8  movwf   0x48                                   ; reg: 0x048
0609:  219e  call    function_006
060a:  3004  movlw   0x04
060b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
060c:  00c9  movwf   0x49                                   ; reg: 0x049

label_070:                                                  ; address: 0x060d

060d:  30fa  movlw   0xfa
060e:  00ce  movwf   0x4e                                   ; reg: 0x04e
060f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0610:  25cc  call    function_024
0611:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0612:  0bc9  decfsz  0x49, F                                ; reg: 0x049
0613:  2e0d  goto    label_070
0614:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0615:  2df2  goto    label_066

label_071:                                                  ; address: 0x0616

0616:  3400  retlw   0x00

label_072:                                                  ; address: 0x0617

0617:  3002  movlw   0x02
0618:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0619:  00c8  movwf   0x48                                   ; reg: 0x048
061a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
061b:  2604  call    function_025
061c:  3071  movlw   0x71
061d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
061e:  00c8  movwf   0x48                                   ; reg: 0x048
061f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0620:  2604  call    function_025
0621:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0622:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
0623:  286e  goto    label_234

function_026:                                               ; address: 0x0624

0624:  0843  movf    0x43, W                                ; reg: 0x043
0625:  390f  andlw   0x0f
0626:  3c00  sublw   0x00
0627:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0628:  2e39  goto    label_367
0629:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
062a:  0853  movf    0x53, W                                ; reg: 0x053
062b:  3c01  sublw   0x01
062c:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
062d:  2e38  goto    label_366
062e:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
062f:  2e34  goto    label_365
0630:  0852  movf    0x52, W                                ; reg: 0x052
0631:  3c67  sublw   0x67
0632:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0633:  2e38  goto    label_366
0634:  3001  movlw   0x01
0635:  00d3  movwf   0x53                                   ; reg: 0x053
0636:  3068  movlw   0x68
0637:  00d2  movwf   0x52                                   ; reg: 0x052
0638:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0639:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
063a:  0852  movf    0x52, W                                ; reg: 0x052
063b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
063c:  0241  subwf   0x41, W                                ; reg: 0x041
063d:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
063e:  2e45  goto    label_369
063f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0640:  0853  movf    0x53, W                                ; reg: 0x053
0641:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0642:  0242  subwf   0x42, W                                ; reg: 0x042
0643:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0644:  2e4d  goto    label_370
0645:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0646:  0853  movf    0x53, W                                ; reg: 0x053
0647:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0648:  00c0  movwf   0x40                                   ; reg: 0x040
0649:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
064a:  0852  movf    0x52, W                                ; reg: 0x052
064b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
064c:  00bf  movwf   0x3f                                   ; reg: 0x03f
064d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
064e:  0853  movf    0x53, W                                ; reg: 0x053
064f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0650:  00c2  movwf   0x42                                   ; reg: 0x042
0651:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0652:  0852  movf    0x52, W                                ; reg: 0x052
0653:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0654:  00c1  movwf   0x41                                   ; reg: 0x041
0655:  12c3  bcf     0x43, 0x5                              ; reg: 0x043
0656:  3400  retlw   0x00

label_073:                                                  ; address: 0x0657

0657:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0658:  0851  movf    0x51, W                                ; reg: 0x051
0659:  00db  movwf   0x5b                                   ; reg: 0x05b
065a:  0850  movf    0x50, W                                ; reg: 0x050
065b:  00da  movwf   0x5a                                   ; reg: 0x05a
065c:  01dd  clrf    0x5d                                   ; reg: 0x05d
065d:  3026  movlw   0x26
065e:  00dc  movwf   0x5c                                   ; reg: 0x05c
065f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0660:  23e7  call    function_064
0661:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0662:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0663:  00d3  movwf   0x53                                   ; reg: 0x053
0664:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0665:  00d2  movwf   0x52                                   ; reg: 0x052
0666:  306e  movlw   0x6e
0667:  00da  movwf   0x5a                                   ; reg: 0x05a
0668:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0669:  23d0  call    0x03d0
066a:  1c78  btfss   (Common_RAM + 8), 0x0                  ; reg: 0x078
066b:  2e7f  goto    0x067f
066c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
066d:  0853  movf    0x53, W                                ; reg: 0x053
066e:  00db  movwf   0x5b                                   ; reg: 0x05b
066f:  0852  movf    0x52, W                                ; reg: 0x052
0670:  00da  movwf   0x5a                                   ; reg: 0x05a
0671:  01dd  clrf    0x5d                                   ; reg: 0x05d
0672:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0673:  082e  movf    0x2e, W                                ; reg: 0x02e
0674:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0675:  00dc  movwf   0x5c                                   ; reg: 0x05c
0676:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0677:  23e7  call    0x03e7
0678:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0679:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
067a:  00d3  movwf   0x53                                   ; reg: 0x053
067b:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
067c:  00d2  movwf   0x52                                   ; reg: 0x052
067d:  2e91  goto    0x0691
067e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
067f:  082f  movf    0x2f, W                                ; reg: 0x02f
0680:  3cff  sublw   0xff
0681:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0682:  00d4  movwf   0x54                                   ; reg: 0x054
0683:  0853  movf    0x53, W                                ; reg: 0x053
0684:  00db  movwf   0x5b                                   ; reg: 0x05b
0685:  0852  movf    0x52, W                                ; reg: 0x052
0686:  00da  movwf   0x5a                                   ; reg: 0x05a
0687:  01dd  clrf    0x5d                                   ; reg: 0x05d
0688:  0854  movf    0x54, W                                ; reg: 0x054
0689:  00dc  movwf   0x5c                                   ; reg: 0x05c
068a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
068b:  23e7  call    0x03e7
068c:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
068d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
068e:  00d3  movwf   0x53                                   ; reg: 0x053
068f:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0690:  00d2  movwf   0x52                                   ; reg: 0x052
0691:  0851  movf    0x51, W                                ; reg: 0x051
0692:  00db  movwf   0x5b                                   ; reg: 0x05b
0693:  0850  movf    0x50, W                                ; reg: 0x050
0694:  00da  movwf   0x5a                                   ; reg: 0x05a
0695:  01dd  clrf    0x5d                                   ; reg: 0x05d
0696:  3059  movlw   0x59
0697:  00dc  movwf   0x5c                                   ; reg: 0x05c
0698:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0699:  23e7  call    0x03e7
069a:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
069b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
069c:  07d2  addwf   0x52, F                                ; reg: 0x052
069d:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
069e:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
069f:  0f79  incfsz  (Common_RAM + 9), W                    ; reg: 0x079
06a0:  07d3  addwf   0x53, F                                ; reg: 0x053
06a1:  0852  movf    0x52, W                                ; reg: 0x052
06a2:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
06a3:  0853  movf    0x53, W                                ; reg: 0x053
06a4:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
06a5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
06a6:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
06a7:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
06a8:  2eb3  goto    label_074

function_027:                                               ; address: 0x06a9

06a9:  1086  bcf     PORTB, RB1                             ; reg: 0x006, bit: 1
06aa:  0842  movf    0x42, W                                ; reg: 0x042
06ab:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
06ac:  00d1  movwf   0x51                                   ; reg: 0x051
06ad:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
06ae:  0841  movf    0x41, W                                ; reg: 0x041
06af:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
06b0:  00d0  movwf   0x50                                   ; reg: 0x050
06b1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
06b2:  2e57  goto    label_073

label_074:                                                  ; address: 0x06b3

06b3:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
06b4:  00c0  movwf   0x40                                   ; reg: 0x040
06b5:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
06b6:  00bf  movwf   0x3f                                   ; reg: 0x03f
06b7:  0845  movf    0x45, W                                ; reg: 0x045
06b8:  0240  subwf   0x40, W                                ; reg: 0x040
06b9:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
06ba:  2ecb  goto    label_076
06bb:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
06bc:  2ec1  goto    label_075
06bd:  083f  movf    0x3f, W                                ; reg: 0x03f
06be:  0244  subwf   0x44, W                                ; reg: 0x044
06bf:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
06c0:  2ecb  goto    label_076

label_075:                                                  ; address: 0x06c1

06c1:  0844  movf    0x44, W                                ; reg: 0x044
06c2:  023f  subwf   0x3f, W                                ; reg: 0x03f
06c3:  00bd  movwf   0x3d                                   ; reg: 0x03d
06c4:  0840  movf    0x40, W                                ; reg: 0x040
06c5:  00be  movwf   0x3e                                   ; reg: 0x03e
06c6:  0845  movf    0x45, W                                ; reg: 0x045
06c7:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
06c8:  0f45  incfsz  0x45, W                                ; reg: 0x045
06c9:  02be  subwf   0x3e, F                                ; reg: 0x03e
06ca:  2ece  goto    label_077

label_076:                                                  ; address: 0x06cb

06cb:  01be  clrf    0x3e                                   ; reg: 0x03e
06cc:  3001  movlw   0x01
06cd:  00bd  movwf   0x3d                                   ; reg: 0x03d

label_077:                                                  ; address: 0x06ce

06ce:  0843  movf    0x43, W                                ; reg: 0x043
06cf:  390f  andlw   0x0f
06d0:  3c00  sublw   0x00
06d1:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
06d2:  2ee1  goto    label_079
06d3:  083e  movf    0x3e, W                                ; reg: 0x03e
06d4:  3c01  sublw   0x01
06d5:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
06d6:  2ee1  goto    label_079
06d7:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
06d8:  2edd  goto    label_078
06d9:  083d  movf    0x3d, W                                ; reg: 0x03d
06da:  3c67  sublw   0x67
06db:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
06dc:  2ee1  goto    label_079

label_078:                                                  ; address: 0x06dd

06dd:  3001  movlw   0x01
06de:  00be  movwf   0x3e                                   ; reg: 0x03e
06df:  3068  movlw   0x68
06e0:  00bd  movwf   0x3d                                   ; reg: 0x03d

label_079:                                                  ; address: 0x06e1

06e1:  083e  movf    0x3e, W                                ; reg: 0x03e
06e2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
06e3:  00d1  movwf   0x51                                   ; reg: 0x051
06e4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
06e5:  083d  movf    0x3d, W                                ; reg: 0x03d
06e6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
06e7:  00d0  movwf   0x50                                   ; reg: 0x050
06e8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
06e9:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6

label_080:                                                  ; address: 0x06ea

06ea:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
06eb:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
06ec:  2eea  goto    label_080
06ed:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
06ee:  0851  movf    0x51, W                                ; reg: 0x051
06ef:  00f2  movwf   (Common_RAM + 2)                       ; reg: 0x072
06f0:  0850  movf    0x50, W                                ; reg: 0x050
06f1:  00f1  movwf   (Common_RAM + 1)                       ; reg: 0x071
06f2:  30c0  movlw   0xc0
06f3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
06f4:  048b  iorwf   INTCON, F                              ; reg: 0x00b
06f5:  3400  retlw   0x00

function_028:                                               ; address: 0x06f6

06f6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
06f7:  01c4  clrf    0x44                                   ; reg: 0x044
06f8:  01c3  clrf    0x43                                   ; reg: 0x043
06f9:  01cf  clrf    0x4f                                   ; reg: 0x04f
06fa:  3002  movlw   0x02
06fb:  00ce  movwf   0x4e                                   ; reg: 0x04e

label_081:                                                  ; address: 0x06fc

06fc:  084f  movf    0x4f, W                                ; reg: 0x04f
06fd:  3c00  sublw   0x00
06fe:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
06ff:  2f1c  goto    label_082
0700:  084e  movf    0x4e, W                                ; reg: 0x04e
0701:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0702:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
0703:  008d  movwf   EEADR                                  ; reg: 0x10d
0704:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0705:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
0706:  140c  bsf     EECON1, RD                             ; reg: 0x18c, bit: 0
0707:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0708:  080c  movf    EEDATA, W                              ; reg: 0x10c
0709:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
070a:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
070b:  07c3  addwf   0x43, F                                ; reg: 0x0c3
070c:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
070d:  0ac4  incf    0x44, F                                ; reg: 0x0c4
070e:  01d0  clrf    0x50                                   ; reg: 0x0d0
070f:  1bc4  btfsc   0x44, 0x7                              ; reg: 0x0c4
0710:  0ad0  incf    0x50, F                                ; reg: 0x0d0
0711:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0712:  0dc3  rlf     0x43, F                                ; reg: 0x0c3
0713:  0dc4  rlf     0x44, F                                ; reg: 0x0c4
0714:  0850  movf    0x50, W                                ; reg: 0x0d0
0715:  07c3  addwf   0x43, F                                ; reg: 0x0c3
0716:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0717:  0ac4  incf    0x44, F                                ; reg: 0x0c4
0718:  0ace  incf    0x4e, F                                ; reg: 0x0ce
0719:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
071a:  0acf  incf    0x4f, F                                ; reg: 0x0cf
071b:  2efc  goto    label_081

label_082:                                                  ; address: 0x071c

071c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
071d:  3400  retlw   0x00

function_029:                                               ; address: 0x071e

071e:  147e  bsf     (Common_RAM + 14), 0x0                 ; reg: 0x07e
071f:  14fe  bsf     (Common_RAM + 14), 0x1                 ; reg: 0x07e
0720:  157e  bsf     (Common_RAM + 14), 0x2                 ; reg: 0x07e
0721:  15fe  bsf     (Common_RAM + 14), 0x3                 ; reg: 0x07e
0722:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
0723:  018d  clrf    PIR2                                   ; reg: 0x00d
0724:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0725:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
0726:  140c  bsf     EECON1, RD                             ; reg: 0x18c, bit: 0
0727:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0728:  080c  movf    EEDATA, W                              ; reg: 0x10c
0729:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
072a:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
072b:  0244  subwf   0x44, W                                ; reg: 0x0c4
072c:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
072d:  2f30  goto    label_083
072e:  107e  bcf     (Common_RAM + 14), 0x0                 ; reg: 0x07e
072f:  10fe  bcf     (Common_RAM + 14), 0x1                 ; reg: 0x07e

label_083:                                                  ; address: 0x0730

0730:  3001  movlw   0x01
0731:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0732:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
0733:  008d  movwf   EEADR                                  ; reg: 0x10d
0734:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0735:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
0736:  140c  bsf     EECON1, RD                             ; reg: 0x18c, bit: 0
0737:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0738:  080c  movf    EEDATA, W                              ; reg: 0x10c
0739:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
073a:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
073b:  0243  subwf   0x43, W                                ; reg: 0x0c3
073c:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
073d:  2f40  goto    label_084
073e:  107e  bcf     (Common_RAM + 14), 0x0                 ; reg: 0x07e
073f:  117e  bcf     (Common_RAM + 14), 0x2                 ; reg: 0x07e

label_084:                                                  ; address: 0x0740

0740:  3002  movlw   0x02
0741:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0742:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
0743:  008d  movwf   EEADR                                  ; reg: 0x10d
0744:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0745:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
0746:  140c  bsf     EECON1, RD                             ; reg: 0x18c, bit: 0
0747:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0748:  080c  movf    EEDATA, W                              ; reg: 0x10c
0749:  3c07  sublw   0x07
074a:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
074b:  2f4e  goto    label_085
074c:  107e  bcf     (Common_RAM + 14), 0x0                 ; reg: 0x07e
074d:  11fe  bcf     (Common_RAM + 14), 0x3                 ; reg: 0x07e

label_085:                                                  ; address: 0x074e

074e:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
074f:  3400  retlw   0x00

function_030:                                               ; address: 0x0750

0750:  26f6  call    function_028
0751:  271e  call    function_029
0752:  3400  retlw   0x00

function_031:                                               ; address: 0x0753

0753:  2750  call    function_030
0754:  087e  movf    (Common_RAM + 14), W                   ; reg: 0x07e
0755:  390f  andlw   0x0f
0756:  3c0f  sublw   0x0f
0757:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0758:  2f5f  goto    label_086
0759:  2750  call    function_030
075a:  087e  movf    (Common_RAM + 14), W                   ; reg: 0x07e
075b:  390f  andlw   0x0f
075c:  3c0f  sublw   0x0f
075d:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
075e:  2f5f  goto    label_086

label_086:                                                  ; address: 0x075f

075f:  3400  retlw   0x00

function_032:                                               ; address: 0x0760

0760:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0761:  0854  movf    0x54, W                                ; reg: 0x054
0762:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0763:  026d  subwf   0x6d, W                                ; reg: 0x06d
0764:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0765:  2f6a  goto    label_087
0766:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0767:  0854  movf    0x54, W                                ; reg: 0x054
0768:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0769:  00ed  movwf   0x6d                                   ; reg: 0x06d

label_087:                                                  ; address: 0x076a

076a:  3400  retlw   0x00

function_033:                                               ; address: 0x076b

076b:  13d6  bcf     0x56, 0x7                              ; reg: 0x056
076c:  21dc  call    function_008
076d:  3400  retlw   0x00

function_034:                                               ; address: 0x076e

076e:  17d6  bsf     0x56, 0x7                              ; reg: 0x056
076f:  21dc  call    function_008
0770:  3400  retlw   0x00

function_035:                                               ; address: 0x0771

0771:  3054  movlw   0x54

label_088:                                                  ; address: 0x0772

0772:  1e0c  btfss   PIR1, TXIF                             ; reg: 0x00c, bit: 4
0773:  2f72  goto    label_088
0774:  0099  movwf   TXREG                                  ; reg: 0x019
0775:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0776:  0854  movf    0x54, W                                ; reg: 0x054
0777:  00d6  movwf   0x56                                   ; reg: 0x056
0778:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0779:  22ad  call    function_013
077a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
077b:  0855  movf    0x55, W                                ; reg: 0x055
077c:  00d6  movwf   0x56                                   ; reg: 0x056
077d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
077e:  22ad  call    function_013
077f:  300a  movlw   0x0a

label_089:                                                  ; address: 0x0780

0780:  1e0c  btfss   PIR1, TXIF                             ; reg: 0x00c, bit: 4
0781:  2f80  goto    label_089
0782:  0099  movwf   TXREG                                  ; reg: 0x019
0783:  3400  retlw   0x00
0784:  0848  movf    0x48, W                                ; reg: 0x048
0785:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0786:  00d3  movwf   0x53                                   ; reg: 0x053
0787:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0788:  01c8  clrf    0x48                                   ; reg: 0x048
0789:  01f3  clrf    (Common_RAM + 3)                       ; reg: 0x073
078a:  13c9  bcf     0x49, 0x7                              ; reg: 0x049
078b:  084c  movf    0x4c, W                                ; reg: 0x04c
078c:  3970  andlw   0x70
078d:  3c2f  sublw   0x2f
078e:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
078f:  2f92  goto    label_090
0790:  1ed0  btfss   0x50, 0x5                              ; reg: 0x050
0791:  2f9b  goto    label_092

label_090:                                                  ; address: 0x0792

0792:  085d  movf    0x5d, W                                ; reg: 0x05d
0793:  3907  andlw   0x07
0794:  00f4  movwf   (Common_RAM + 4)                       ; reg: 0x074
0795:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074

label_091:                                                  ; address: 0x0796

0796:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0797:  0dc8  rlf     0x48, F                                ; reg: 0x048
0798:  0ac8  incf    0x48, F                                ; reg: 0x048
0799:  0bf4  decfsz  (Common_RAM + 4), F                    ; reg: 0x074
079a:  2f96  goto    label_091

label_092:                                                  ; address: 0x079b

079b:  08cf  movf    0x4f, F                                ; reg: 0x04f
079c:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
079d:  2fa1  goto    label_093
079e:  17c9  bsf     0x49, 0x7                              ; reg: 0x049
079f:  084f  movf    0x4f, W                                ; reg: 0x04f
07a0:  04f3  iorwf   (Common_RAM + 3), F                    ; reg: 0x073

label_093:                                                  ; address: 0x07a1

07a1:  182d  btfsc   0x2d, 0x0                              ; reg: 0x02d
07a2:  2fa5  goto    label_094
07a3:  3041  movlw   0x41
07a4:  04f3  iorwf   (Common_RAM + 3), F                    ; reg: 0x073

label_094:                                                  ; address: 0x07a5

07a5:  18ad  btfsc   0x2d, 0x1                              ; reg: 0x02d
07a6:  2fa9  goto    label_095
07a7:  3042  movlw   0x42
07a8:  04f3  iorwf   (Common_RAM + 3), F                    ; reg: 0x073

label_095:                                                  ; address: 0x07a9

07a9:  1c30  btfss   0x30, 0x0                              ; reg: 0x030
07aa:  2fad  goto    label_096
07ab:  17c9  bsf     0x49, 0x7                              ; reg: 0x049
07ac:  1673  bsf     (Common_RAM + 3), 0x4                  ; reg: 0x073

label_096:                                                  ; address: 0x07ad

07ad:  1e50  btfss   0x50, 0x4                              ; reg: 0x050
07ae:  2fb2  goto    label_097
07af:  17c9  bsf     0x49, 0x7                              ; reg: 0x049
07b0:  3006  movlw   0x06
07b1:  04f3  iorwf   (Common_RAM + 3), F                    ; reg: 0x073

label_097:                                                  ; address: 0x07b2

07b2:  0843  movf    0x43, W                                ; reg: 0x043
07b3:  390f  andlw   0x0f
07b4:  3c01  sublw   0x01
07b5:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
07b6:  2fbe  goto    label_098
07b7:  17c9  bsf     0x49, 0x7                              ; reg: 0x049
07b8:  17f3  bsf     (Common_RAM + 3), 0x7                  ; reg: 0x073
07b9:  3005  movlw   0x05
07ba:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
07bb:  00d4  movwf   0x54                                   ; reg: 0x054
07bc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
07bd:  2760  call    function_032

label_098:                                                  ; address: 0x07be

07be:  0873  movf    (Common_RAM + 3), W                    ; reg: 0x073
07bf:  04c8  iorwf   0x48, F                                ; reg: 0x048
07c0:  1d49  btfss   0x49, 0x2                              ; reg: 0x049
07c1:  2fcd  goto    label_101
07c2:  18d0  btfsc   0x50, 0x1                              ; reg: 0x050
07c3:  2fc9  goto    label_099
07c4:  084c  movf    0x4c, W                                ; reg: 0x04c
07c5:  3970  andlw   0x70
07c6:  3c60  sublw   0x60
07c7:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
07c8:  2fcd  goto    label_101

label_099:                                                  ; address: 0x07c9

07c9:  1fd6  btfss   0x56, 0x7                              ; reg: 0x056
07ca:  2fcc  goto    label_100
07cb:  276b  call    function_033

label_100:                                                  ; address: 0x07cc

07cc:  2fd0  goto    label_102

label_101:                                                  ; address: 0x07cd

07cd:  1bd6  btfsc   0x56, 0x7                              ; reg: 0x056
07ce:  2fd0  goto    label_102
07cf:  276e  call    function_034

label_102:                                                  ; address: 0x07d0

07d0:  1dcc  btfss   0x4c, 0x3                              ; reg: 0x04c
07d1:  2fd5  goto    label_103
07d2:  0848  movf    0x48, W                                ; reg: 0x048
07d3:  04f3  iorwf   (Common_RAM + 3), F                    ; reg: 0x073
07d4:  13c9  bcf     0x49, 0x7                              ; reg: 0x049

label_103:                                                  ; address: 0x07d5

07d5:  1e49  btfss   0x49, 0x4                              ; reg: 0x049
07d6:  2fd9  goto    label_104
07d7:  0873  movf    (Common_RAM + 3), W                    ; reg: 0x073
07d8:  06c8  xorwf   0x48, F                                ; reg: 0x048

label_104:                                                  ; address: 0x07d9

07d9:  219e  call    function_006
07da:  0848  movf    0x48, W                                ; reg: 0x048
07db:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
07dc:  0253  subwf   0x53, W                                ; reg: 0x053
07dd:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
07de:  2feb  goto    label_105
07df:  08c2  movf    0x42, F                                ; reg: 0x042
07e0:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
07e1:  2feb  goto    label_105
07e2:  3020  movlw   0x20
07e3:  00d4  movwf   0x54                                   ; reg: 0x054
07e4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
07e5:  0848  movf    0x48, W                                ; reg: 0x048
07e6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
07e7:  00d5  movwf   0x55                                   ; reg: 0x055
07e8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
07e9:  2771  call    function_035
07ea:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_105:                                                  ; address: 0x07eb

07eb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
07ec:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
07ed:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
07ee:  28c8  goto    label_114
07ef:  084c  movf    0x4c, W                                ; reg: 0x04c
07f0:  3970  andlw   0x70
07f1:  3c3f  sublw   0x3f
07f2:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
07f3:  2ffb  goto    label_137
07f4:  084c  movf    0x4c, W                                ; reg: 0x04c
07f5:  3970  andlw   0x70
07f6:  3c5f  sublw   0x5f
07f7:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
07f8:  2ffb  goto    label_137
07f9:  3007  movlw   0x07
07fa:  00ad  movwf   0x2d                                   ; reg: 0x02d
07fb:  3400  retlw   0x00

function_036:                                               ; address: 0x0800

0800:  1d0c  btfss   PIR1, CCP1IF                           ; reg: 0x00c, bit: 2
0801:  28c4  goto    label_113
0802:  110c  bcf     PIR1, CCP1IF                           ; reg: 0x00c, bit: 2
0803:  3001  movlw   0x01
0804:  1bc9  btfsc   0x49, 0x7                              ; reg: 0x049
0805:  3004  movlw   0x04
0806:  07c9  addwf   0x49, F                                ; reg: 0x049
0807:  12c9  bcf     0x49, 0x5                              ; reg: 0x049
0808:  0abb  incf    0x3b, F                                ; reg: 0x03b
0809:  0f3c  incfsz  0x3c, W                                ; reg: 0x03c
080a:  00bc  movwf   0x3c                                   ; reg: 0x03c
080b:  30f0  movlw   0xf0
080c:  1c89  btfss   PORTE, RE1                             ; reg: 0x009, bit: 1
080d:  1c86  btfss   PORTB, RB1                             ; reg: 0x006, bit: 1
080e:  05bb  andwf   0x3b, F                                ; reg: 0x03b
080f:  0854  movf    0x54, W                                ; reg: 0x054
0810:  3c07  sublw   0x07
0811:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0812:  2815  goto    label_106
0813:  0ad5  incf    0x55, F                                ; reg: 0x055
0814:  17dd  bsf     0x5d, 0x7                              ; reg: 0x05d

label_106:                                                  ; address: 0x0815

0815:  1c98  btfss   RCSTA, OERR                            ; reg: 0x018, bit: 1
0816:  281a  goto    label_107
0817:  1098  bcf     RCSTA, OERR                            ; reg: 0x018, bit: 1
0818:  1218  bcf     RCSTA, CREN                            ; reg: 0x018, bit: 4
0819:  1618  bsf     RCSTA, CREN                            ; reg: 0x018, bit: 4

label_107:                                                  ; address: 0x081a

081a:  08ce  movf    0x4e, F                                ; reg: 0x04e
081b:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
081c:  2820  goto    label_108
081d:  03ce  decf    0x4e, F                                ; reg: 0x04e
081e:  15cc  bsf     0x4c, 0x3                              ; reg: 0x04c
081f:  2821  goto    label_109

label_108:                                                  ; address: 0x0820

0820:  11cc  bcf     0x4c, 0x3                              ; reg: 0x04c

label_109:                                                  ; address: 0x0821

0821:  1c4a  btfss   0x4a, 0x0                              ; reg: 0x04a
0822:  2824  goto    label_110
0823:  0adf  incf    0x5f, F                                ; reg: 0x05f

label_110:                                                  ; address: 0x0824

0824:  1c4a  btfss   0x4a, 0x0                              ; reg: 0x04a
0825:  2834  goto    label_111
0826:  1cca  btfss   0x4a, 0x1                              ; reg: 0x04a
0827:  2834  goto    label_111
0828:  1d4a  btfss   0x4a, 0x2                              ; reg: 0x04a
0829:  2834  goto    label_111
082a:  1dca  btfss   0x4a, 0x3                              ; reg: 0x04a
082b:  2834  goto    label_111
082c:  1e4a  btfss   0x4a, 0x4                              ; reg: 0x04a
082d:  2834  goto    label_111
082e:  0ade  incf    0x5e, F                                ; reg: 0x05e
082f:  0ae0  incf    0x60, F                                ; reg: 0x060
0830:  08ed  movf    0x6d, F                                ; reg: 0x06d
0831:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0832:  2834  goto    label_111
0833:  03ed  decf    0x6d, F                                ; reg: 0x06d

label_111:                                                  ; address: 0x0834

0834:  0af0  incf    Common_RAM, F                          ; reg: 0x070
0835:  1a51  btfsc   0x51, 0x4                              ; reg: 0x051
0836:  283b  goto    label_112
0837:  0fca  incfsz  0x4a, F                                ; reg: 0x04a
0838:  283b  goto    label_112
0839:  0f4b  incfsz  0x4b, W                                ; reg: 0x04b
083a:  00cb  movwf   0x4b                                   ; reg: 0x04b

label_112:                                                  ; address: 0x083b

083b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
083c:  22f6  call    function_015
083d:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
083e:  1c86  btfss   PORTB, RB1                             ; reg: 0x006, bit: 1
083f:  2847  goto    0x0047
0840:  1808  btfsc   PORTD, RD0                             ; reg: 0x008, bit: 0
0841:  2846  goto    0x0046
0842:  1e43  btfss   0x43, 0x4                              ; reg: 0x043
0843:  2845  goto    0x0045
0844:  17c3  bsf     0x43, 0x7                              ; reg: 0x043
0845:  2847  goto    0x0047
0846:  1643  bsf     0x43, 0x4                              ; reg: 0x043
0847:  08b3  movf    0x33, F                                ; reg: 0x033
0848:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0849:  284e  goto    0x004e
084a:  1186  bcf     PORTB, RB3                             ; reg: 0x006, bit: 3
084b:  01b7  clrf    0x37                                   ; reg: 0x037
084c:  01b8  clrf    0x38                                   ; reg: 0x038
084d:  28b2  goto    0x00b2
084e:  1bb5  btfsc   0x35, 0x7                              ; reg: 0x035
084f:  2851  goto    0x0051
0850:  28b2  goto    0x00b2
0851:  13b5  bcf     0x35, 0x7                              ; reg: 0x035
0852:  083c  movf    0x3c, W                                ; reg: 0x03c
0853:  3c09  sublw   0x09
0854:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0855:  2858  goto    0x0058
0856:  0abc  incf    0x3c, F                                ; reg: 0x03c
0857:  28b2  goto    0x00b2
0858:  01bc  clrf    0x3c                                   ; reg: 0x03c
0859:  0834  movf    0x34, W                                ; reg: 0x034
085a:  3c04  sublw   0x04
085b:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
085c:  2869  goto    0x0069
085d:  1f3b  btfss   0x3b, 0x6                              ; reg: 0x03b
085e:  2862  goto    0x0062
085f:  16cf  bsf     0x4f, 0x5                              ; reg: 0x04f

function_037:                                               ; address: 0x0860

0860:  17b0  bsf     0x30, 0x7                              ; reg: 0x030
0861:  2864  goto    0x0064
0862:  3010  movlw   0x10
0863:  07bb  addwf   0x3b, F                                ; reg: 0x03b
0864:  30ff  movlw   0xff
0865:  00bc  movwf   0x3c                                   ; reg: 0x03c
0866:  3002  movlw   0x02
0867:  00b7  movwf   0x37                                   ; reg: 0x037
0868:  28b2  goto    0x00b2
0869:  300f  movlw   0x0f
086a:  05bb  andwf   0x3b, F                                ; reg: 0x03b
086b:  0f33  incfsz  0x33, W                                ; reg: 0x033
086c:  2870  goto    0x0070
086d:  3001  movlw   0x01
086e:  00b7  movwf   0x37                                   ; reg: 0x037
086f:  28b2  goto    0x00b2
0870:  0833  movf    0x33, W                                ; reg: 0x033
0871:  0234  subwf   0x34, W                                ; reg: 0x034
0872:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0873:  2875  goto    0x0075
0874:  28b2  goto    0x00b2
0875:  0833  movf    0x33, W                                ; reg: 0x033
0876:  0234  subwf   0x34, W                                ; reg: 0x034
0877:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0878:  2890  goto    0x0090
0879:  08b7  movf    0x37, F                                ; reg: 0x037
087a:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
087b:  287d  goto    0x007d
087c:  03b7  decf    0x37, F                                ; reg: 0x037
087d:  0834  movf    0x34, W                                ; reg: 0x034
087e:  0236  subwf   0x36, W                                ; reg: 0x036
087f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0880:  288b  goto    0x008b
0881:  0834  movf    0x34, W                                ; reg: 0x034
0882:  0236  subwf   0x36, W                                ; reg: 0x036
0883:  3c0a  sublw   0x0a
0884:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0885:  288a  goto    0x008a
0886:  08b7  movf    0x37, F                                ; reg: 0x037
0887:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0888:  288a  goto    0x008a
0889:  03b7  decf    0x37, F                                ; reg: 0x037
088a:  288f  goto    0x008f
088b:  0f37  incfsz  0x37, W                                ; reg: 0x037
088c:  288e  goto    0x008e
088d:  288f  goto    0x008f
088e:  0ab7  incf    0x37, F                                ; reg: 0x037
088f:  28aa  goto    0x00aa
0890:  0834  movf    0x34, W                                ; reg: 0x034
0891:  0233  subwf   0x33, W                                ; reg: 0x033
0892:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0893:  28aa  goto    0x00aa
0894:  0f37  incfsz  0x37, W                                ; reg: 0x037
0895:  2897  goto    0x0097
0896:  2898  goto    0x0098
0897:  0ab7  incf    0x37, F                                ; reg: 0x037
0898:  0836  movf    0x36, W                                ; reg: 0x036
0899:  0234  subwf   0x34, W                                ; reg: 0x034
089a:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
089b:  28a6  goto    0x00a6
089c:  0836  movf    0x36, W                                ; reg: 0x036
089d:  0234  subwf   0x34, W                                ; reg: 0x034
089e:  3c0a  sublw   0x0a
089f:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
08a0:  28a5  goto    0x00a5
08a1:  0f37  incfsz  0x37, W                                ; reg: 0x037
08a2:  28a4  goto    0x00a4
08a3:  28a5  goto    0x00a5
08a4:  0ab7  incf    0x37, F                                ; reg: 0x037
08a5:  28aa  goto    0x00aa
08a6:  08b7  movf    0x37, F                                ; reg: 0x037
08a7:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
08a8:  28aa  goto    0x00aa
08a9:  03b7  decf    0x37, F                                ; reg: 0x037
08aa:  0834  movf    0x34, W                                ; reg: 0x034
08ab:  00b6  movwf   0x36                                   ; reg: 0x036
08ac:  08b7  movf    0x37, F                                ; reg: 0x037
08ad:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
08ae:  28b2  goto    0x00b2
08af:  3001  movlw   0x01
08b0:  00b7  movwf   0x37                                   ; reg: 0x037
08b1:  28b2  goto    0x00b2
08b2:  1e06  btfss   PORTB, RB4                             ; reg: 0x006, bit: 4
08b3:  28b6  goto    0x00b6
08b4:  300c  movlw   0x0c
08b5:  00ce  movwf   0x4e                                   ; reg: 0x04e
08b6:  0857  movf    0x57, W                                ; reg: 0x057
08b7:  3cfc  sublw   0xfc
08b8:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
08b9:  28bb  goto    0x00bb
08ba:  1450  bsf     0x50, 0x0                              ; reg: 0x050
08bb:  1c50  btfss   0x50, 0x0                              ; reg: 0x050
08bc:  28c4  goto    0x00c4
08bd:  0857  movf    0x57, W                                ; reg: 0x057
08be:  3cf4  sublw   0xf4
08bf:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
08c0:  28c3  goto    0x00c3
08c1:  1050  bcf     0x50, 0x0                              ; reg: 0x050
08c2:  28c4  goto    0x00c4
08c3:  15cc  bsf     0x4c, 0x3                              ; reg: 0x04c

label_113:                                                  ; address: 0x08c4

08c4:  19d1  btfsc   0x51, 0x3                              ; reg: 0x051
08c5:  28c9  goto    0x00c9
08c6:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
08c7:  2f84  goto    0x0784

label_114:                                                  ; address: 0x08c8

08c8:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
08c9:  3400  retlw   0x00

function_038:                                               ; address: 0x08ca

08ca:  1c7e  btfss   (Common_RAM + 14), 0x0                 ; reg: 0x07e
08cb:  28e1  goto    0x00e1
08cc:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
08cd:  0856  movf    0x56, W                                ; reg: 0x056
08ce:  00da  movwf   0x5a                                   ; reg: 0x05a
08cf:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
08d0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
08d1:  23d0  call    0x03d0
08d2:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
08d3:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
08d4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
08d5:  00d7  movwf   0x57                                   ; reg: 0x057
08d6:  0857  movf    0x57, W                                ; reg: 0x057
08d7:  3c64  sublw   0x64
08d8:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
08d9:  28dc  goto    0x00dc
08da:  3064  movlw   0x64
08db:  00d7  movwf   0x57                                   ; reg: 0x057
08dc:  0857  movf    0x57, W                                ; reg: 0x057
08dd:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
08de:  28e5  goto    0x00e5
08df:  28e5  goto    0x00e5
08e0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
08e1:  3064  movlw   0x64
08e2:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
08e3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
08e4:  28e5  goto    0x00e5
08e5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
08e6:  3400  retlw   0x00

function_039:                                               ; address: 0x08e7

08e7:  3020  movlw   0x20
08e8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
08e9:  00e4  movwf   0x64                                   ; reg: 0x064
08ea:  01e0  clrf    0x60                                   ; reg: 0x060
08eb:  01e1  clrf    0x61                                   ; reg: 0x061
08ec:  01e2  clrf    0x62                                   ; reg: 0x062
08ed:  01e3  clrf    0x63                                   ; reg: 0x063
08ee:  085b  movf    0x5b, W                                ; reg: 0x05b
08ef:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
08f0:  085a  movf    0x5a, W                                ; reg: 0x05a
08f1:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
08f2:  0859  movf    0x59, W                                ; reg: 0x059
08f3:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
08f4:  0858  movf    0x58, W                                ; reg: 0x058
08f5:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
08f6:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
08f7:  1c77  btfss   (Common_RAM + 7), 0x0                  ; reg: 0x077
08f8:  2907  goto    0x0107
08f9:  085c  movf    0x5c, W                                ; reg: 0x05c
08fa:  07e0  addwf   0x60, F                                ; reg: 0x060
08fb:  085d  movf    0x5d, W                                ; reg: 0x05d
08fc:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
08fd:  0f5d  incfsz  0x5d, W                                ; reg: 0x05d
08fe:  07e1  addwf   0x61, F                                ; reg: 0x061
08ff:  085e  movf    0x5e, W                                ; reg: 0x05e
0900:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0901:  0f5e  incfsz  0x5e, W                                ; reg: 0x05e
0902:  07e2  addwf   0x62, F                                ; reg: 0x062
0903:  085f  movf    0x5f, W                                ; reg: 0x05f
0904:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0905:  0f5f  incfsz  0x5f, W                                ; reg: 0x05f
0906:  07e3  addwf   0x63, F                                ; reg: 0x063
0907:  0ce3  rrf     0x63, F                                ; reg: 0x063
0908:  0ce2  rrf     0x62, F                                ; reg: 0x062
0909:  0ce1  rrf     0x61, F                                ; reg: 0x061
090a:  0ce0  rrf     0x60, F                                ; reg: 0x060
090b:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
090c:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
090d:  0cf8  rrf     (Common_RAM + 8), F                    ; reg: 0x078
090e:  0cf7  rrf     (Common_RAM + 7), F                    ; reg: 0x077
090f:  0be4  decfsz  0x64, F                                ; reg: 0x064
0910:  28f6  goto    0x00f6
0911:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0912:  3400  retlw   0x00

function_040:                                               ; address: 0x0913

0913:  3064  movlw   0x64
0914:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0915:  00d6  movwf   0x56                                   ; reg: 0x056
0916:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0917:  20ca  call    0x00ca
0918:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0919:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
091a:  00d5  movwf   0x55                                   ; reg: 0x055
091b:  01d7  clrf    0x57                                   ; reg: 0x057
091c:  30a0  movlw   0xa0
091d:  00d6  movwf   0x56                                   ; reg: 0x056
091e:  01d9  clrf    0x59                                   ; reg: 0x059
091f:  0855  movf    0x55, W                                ; reg: 0x055
0920:  00d8  movwf   0x58                                   ; reg: 0x058
0921:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0922:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0923:  23b9  call    0x03b9
0924:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0925:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0926:  01d4  clrf    0x54                                   ; reg: 0x054
0927:  01d3  clrf    0x53                                   ; reg: 0x053
0928:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0929:  00d2  movwf   0x52                                   ; reg: 0x052
092a:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
092b:  00d1  movwf   0x51                                   ; reg: 0x051
092c:  306e  movlw   0x6e
092d:  00da  movwf   0x5a                                   ; reg: 0x05a
092e:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
092f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0930:  23d0  call    0x03d0
0931:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0932:  1c78  btfss   (Common_RAM + 8), 0x0                  ; reg: 0x078
0933:  29ca  goto    0x01ca
0934:  082f  movf    0x2f, W                                ; reg: 0x02f
0935:  3c7f  sublw   0x7f
0936:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0937:  2962  goto    0x0162
0938:  3080  movlw   0x80
0939:  022f  subwf   0x2f, W                                ; reg: 0x02f
093a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
093b:  00d6  movwf   0x56                                   ; reg: 0x056
093c:  01db  clrf    0x5b                                   ; reg: 0x05b
093d:  0856  movf    0x56, W                                ; reg: 0x056
093e:  00da  movwf   0x5a                                   ; reg: 0x05a
093f:  01dd  clrf    0x5d                                   ; reg: 0x05d
0940:  3078  movlw   0x78
0941:  00dc  movwf   0x5c                                   ; reg: 0x05c
0942:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0943:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0944:  23e7  call    0x03e7
0945:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0946:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0947:  3c80  sublw   0x80
0948:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0949:  00d5  movwf   0x55                                   ; reg: 0x055
094a:  0852  movf    0x52, W                                ; reg: 0x052
094b:  00d7  movwf   0x57                                   ; reg: 0x057
094c:  0851  movf    0x51, W                                ; reg: 0x051
094d:  00d6  movwf   0x56                                   ; reg: 0x056
094e:  0852  movf    0x52, W                                ; reg: 0x052
094f:  00db  movwf   0x5b                                   ; reg: 0x05b
0950:  0851  movf    0x51, W                                ; reg: 0x051
0951:  00da  movwf   0x5a                                   ; reg: 0x05a
0952:  01dd  clrf    0x5d                                   ; reg: 0x05d
0953:  0855  movf    0x55, W                                ; reg: 0x055
0954:  00dc  movwf   0x5c                                   ; reg: 0x05c
0955:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0956:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0957:  23e7  call    0x03e7
0958:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0959:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
095a:  01d4  clrf    0x54                                   ; reg: 0x054
095b:  01d3  clrf    0x53                                   ; reg: 0x053
095c:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
095d:  00d2  movwf   0x52                                   ; reg: 0x052
095e:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
095f:  00d1  movwf   0x51                                   ; reg: 0x051
0960:  299d  goto    0x019d
0961:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0962:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0963:  01db  clrf    0x5b                                   ; reg: 0x05b
0964:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0965:  082f  movf    0x2f, W                                ; reg: 0x02f
0966:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0967:  00da  movwf   0x5a                                   ; reg: 0x05a
0968:  01dd  clrf    0x5d                                   ; reg: 0x05d
0969:  3030  movlw   0x30
096a:  00dc  movwf   0x5c                                   ; reg: 0x05c
096b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
096c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
096d:  23e7  call    0x03e7
096e:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
096f:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0970:  3c40  sublw   0x40
0971:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0972:  00d5  movwf   0x55                                   ; reg: 0x055
0973:  0854  movf    0x54, W                                ; reg: 0x054
0974:  00db  movwf   0x5b                                   ; reg: 0x05b
0975:  0853  movf    0x53, W                                ; reg: 0x053
0976:  00da  movwf   0x5a                                   ; reg: 0x05a
0977:  0852  movf    0x52, W                                ; reg: 0x052
0978:  00d9  movwf   0x59                                   ; reg: 0x059
0979:  0851  movf    0x51, W                                ; reg: 0x051
097a:  00d8  movwf   0x58                                   ; reg: 0x058
097b:  01df  clrf    0x5f                                   ; reg: 0x05f
097c:  01de  clrf    0x5e                                   ; reg: 0x05e
097d:  01dd  clrf    0x5d                                   ; reg: 0x05d
097e:  0855  movf    0x55, W                                ; reg: 0x055
097f:  00dc  movwf   0x5c                                   ; reg: 0x05c
0980:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0981:  20e7  call    0x00e7
0982:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
0983:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0984:  00d4  movwf   0x54                                   ; reg: 0x054
0985:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0986:  00d3  movwf   0x53                                   ; reg: 0x053
0987:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0988:  00d2  movwf   0x52                                   ; reg: 0x052
0989:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
098a:  00d1  movwf   0x51                                   ; reg: 0x051
098b:  0cd4  rrf     0x54, F                                ; reg: 0x054
098c:  0cd3  rrf     0x53, F                                ; reg: 0x053
098d:  0cd2  rrf     0x52, F                                ; reg: 0x052
098e:  0cd1  rrf     0x51, F                                ; reg: 0x051
098f:  0cd4  rrf     0x54, F                                ; reg: 0x054
0990:  0cd3  rrf     0x53, F                                ; reg: 0x053
0991:  0cd2  rrf     0x52, F                                ; reg: 0x052
0992:  0cd1  rrf     0x51, F                                ; reg: 0x051
0993:  0cd4  rrf     0x54, F                                ; reg: 0x054
0994:  0cd3  rrf     0x53, F                                ; reg: 0x053
0995:  0cd2  rrf     0x52, F                                ; reg: 0x052
0996:  0cd1  rrf     0x51, F                                ; reg: 0x051
0997:  0cd4  rrf     0x54, F                                ; reg: 0x054
0998:  0cd3  rrf     0x53, F                                ; reg: 0x053
0999:  0cd2  rrf     0x52, F                                ; reg: 0x052
099a:  0cd1  rrf     0x51, F                                ; reg: 0x051
099b:  300f  movlw   0x0f
099c:  05d4  andwf   0x54, F                                ; reg: 0x054
099d:  08d4  movf    0x54, F                                ; reg: 0x054
099e:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
099f:  29ae  goto    0x01ae
09a0:  08d3  movf    0x53, F                                ; reg: 0x053
09a1:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
09a2:  29ae  goto    0x01ae
09a3:  0852  movf    0x52, W                                ; reg: 0x052
09a4:  3cf9  sublw   0xf9
09a5:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
09a6:  29b3  goto    0x01b3
09a7:  3aff  xorlw   0xff
09a8:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
09a9:  29ae  goto    0x01ae
09aa:  0851  movf    0x51, W                                ; reg: 0x051
09ab:  3c00  sublw   0x00
09ac:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
09ad:  29b3  goto    0x01b3
09ae:  01d4  clrf    0x54                                   ; reg: 0x054
09af:  01d3  clrf    0x53                                   ; reg: 0x053
09b0:  30fa  movlw   0xfa
09b1:  00d2  movwf   0x52                                   ; reg: 0x052
09b2:  01d1  clrf    0x51                                   ; reg: 0x051
09b3:  08d4  movf    0x54, F                                ; reg: 0x054
09b4:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
09b5:  29c9  goto    0x01c9
09b6:  08d3  movf    0x53, F                                ; reg: 0x053
09b7:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
09b8:  29c9  goto    0x01c9
09b9:  0852  movf    0x52, W                                ; reg: 0x052
09ba:  3c03  sublw   0x03
09bb:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
09bc:  29c9  goto    0x01c9
09bd:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
09be:  29c3  goto    0x01c3
09bf:  0851  movf    0x51, W                                ; reg: 0x051
09c0:  3ce7  sublw   0xe7
09c1:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
09c2:  29c9  goto    0x01c9
09c3:  01d4  clrf    0x54                                   ; reg: 0x054
09c4:  01d3  clrf    0x53                                   ; reg: 0x053
09c5:  3003  movlw   0x03
09c6:  00d2  movwf   0x52                                   ; reg: 0x052
09c7:  30e8  movlw   0xe8
09c8:  00d1  movwf   0x51                                   ; reg: 0x051
09c9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
09ca:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
09cb:  0851  movf    0x51, W                                ; reg: 0x051
09cc:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
09cd:  0852  movf    0x52, W                                ; reg: 0x052
09ce:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
09cf:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
09d0:  3400  retlw   0x00
09d1:  084c  movf    0x4c, W                                ; reg: 0x04c
09d2:  3907  andlw   0x07
09d3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
09d4:  00cd  movwf   0x4d                                   ; reg: 0x04d
09d5:  084d  movf    0x4d, W                                ; reg: 0x04d
09d6:  00ce  movwf   0x4e                                   ; reg: 0x04e
09d7:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
09d8:  1e4c  btfss   0x4c, 0x4                              ; reg: 0x04c
09d9:  29e1  goto    0x01e1
09da:  0876  movf    (Common_RAM + 6), W                    ; reg: 0x076
09db:  0275  subwf   (Common_RAM + 5), W                    ; reg: 0x075
09dc:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
09dd:  29e1  goto    0x01e1
09de:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
09df:  0ace  incf    0x4e, F                                ; reg: 0x04e
09e0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
09e1:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
09e2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
09e3:  0d4d  rlf     0x4d, W                                ; reg: 0x04d
09e4:  3e12  addlw   0x12
09e5:  00d1  movwf   0x51                                   ; reg: 0x051
09e6:  084e  movf    0x4e, W                                ; reg: 0x04e
09e7:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
09e8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
09e9:  2045  call    0x0045
09ea:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
09eb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
09ec:  00d2  movwf   0x52                                   ; reg: 0x052
09ed:  084d  movf    0x4d, W                                ; reg: 0x04d
09ee:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
09ef:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
09f0:  2045  call    0x0045
09f1:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
09f2:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
09f3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
09f4:  0252  subwf   0x52, W                                ; reg: 0x052
09f5:  0751  addwf   0x51, W                                ; reg: 0x051
09f6:  00cc  movwf   0x4c                                   ; reg: 0x04c
09f7:  084d  movf    0x4d, W                                ; reg: 0x04d
09f8:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
09f9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
09fa:  2045  call    0x0045
09fb:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
09fc:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
09fd:  026b  subwf   0x6b, W                                ; reg: 0x06b
09fe:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
09ff:  0ef7  swapf   (Common_RAM + 7), F                    ; reg: 0x077
0a00:  300f  movlw   0x0f
0a01:  05f7  andwf   (Common_RAM + 7), F                    ; reg: 0x077
0a02:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
0a03:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a04:  07cc  addwf   0x4c, F                                ; reg: 0x04c
0a05:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a06:  2113  call    0x0113
0a07:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0a08:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a09:  00d2  movwf   0x52                                   ; reg: 0x052
0a0a:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0a0b:  00d1  movwf   0x51                                   ; reg: 0x051
0a0c:  0c52  rrf     0x52, W                                ; reg: 0x052
0a0d:  00d0  movwf   0x50                                   ; reg: 0x050
0a0e:  0c51  rrf     0x51, W                                ; reg: 0x051
0a0f:  00cf  movwf   0x4f                                   ; reg: 0x04f
0a10:  0cd0  rrf     0x50, F                                ; reg: 0x050
0a11:  0ccf  rrf     0x4f, F                                ; reg: 0x04f
0a12:  0cd0  rrf     0x50, F                                ; reg: 0x050
0a13:  0ccf  rrf     0x4f, F                                ; reg: 0x04f
0a14:  301f  movlw   0x1f
0a15:  05d0  andwf   0x50, F                                ; reg: 0x050
0a16:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a17:  083a  movf    0x3a, W                                ; reg: 0x03a
0a18:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a19:  0250  subwf   0x50, W                                ; reg: 0x050
0a1a:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0a1b:  2a4e  goto    0x024e
0a1c:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0a1d:  2a26  goto    0x0226
0a1e:  084f  movf    0x4f, W                                ; reg: 0x04f
0a1f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a20:  0239  subwf   0x39, W                                ; reg: 0x039
0a21:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0a22:  2a25  goto    0x0225
0a23:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a24:  2a4e  goto    0x024e
0a25:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a26:  0cd0  rrf     0x50, F                                ; reg: 0x050
0a27:  0ccf  rrf     0x4f, F                                ; reg: 0x04f
0a28:  0cd0  rrf     0x50, F                                ; reg: 0x050
0a29:  0ccf  rrf     0x4f, F                                ; reg: 0x04f
0a2a:  0cd0  rrf     0x50, F                                ; reg: 0x050
0a2b:  0ccf  rrf     0x4f, F                                ; reg: 0x04f
0a2c:  301f  movlw   0x1f
0a2d:  05d0  andwf   0x50, F                                ; reg: 0x050
0a2e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a2f:  083a  movf    0x3a, W                                ; reg: 0x03a
0a30:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a31:  00d5  movwf   0x55                                   ; reg: 0x055
0a32:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a33:  0839  movf    0x39, W                                ; reg: 0x039
0a34:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a35:  00d4  movwf   0x54                                   ; reg: 0x054
0a36:  0850  movf    0x50, W                                ; reg: 0x050
0a37:  00d7  movwf   0x57                                   ; reg: 0x057
0a38:  084f  movf    0x4f, W                                ; reg: 0x04f
0a39:  00d6  movwf   0x56                                   ; reg: 0x056
0a3a:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0a3b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a3c:  24a2  call    0x04a2
0a3d:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0a3e:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0a3f:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
0a40:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0a41:  3c0a  sublw   0x0a
0a42:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0a43:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0a44:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0a45:  0f79  incfsz  (Common_RAM + 9), W                    ; reg: 0x079
0a46:  2a49  goto    0x0249
0a47:  3000  movlw   0x00
0a48:  2a4a  goto    0x024a
0a49:  3c00  sublw   0x00
0a4a:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
0a4b:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
0a4c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a4d:  07cc  addwf   0x4c, F                                ; reg: 0x04c
0a4e:  084c  movf    0x4c, W                                ; reg: 0x04c
0a4f:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0a50:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a51:  3400  retlw   0x00
0a52:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a53:  084e  movf    0x4e, W                                ; reg: 0x04e
0a54:  01f8  clrf    (Common_RAM + 8)                       ; reg: 0x078
0a55:  024d  subwf   0x4d, W                                ; reg: 0x04d
0a56:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0a57:  2a5b  goto    0x025b
0a58:  084d  movf    0x4d, W                                ; reg: 0x04d
0a59:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0a5a:  2a67  goto    0x0267
0a5b:  01f7  clrf    (Common_RAM + 7)                       ; reg: 0x077
0a5c:  3008  movlw   0x08
0a5d:  00cf  movwf   0x4f                                   ; reg: 0x04f
0a5e:  0dcd  rlf     0x4d, F                                ; reg: 0x04d
0a5f:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
0a60:  084e  movf    0x4e, W                                ; reg: 0x04e
0a61:  0277  subwf   (Common_RAM + 7), W                    ; reg: 0x077
0a62:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0a63:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0a64:  0df8  rlf     (Common_RAM + 8), F                    ; reg: 0x078
0a65:  0bcf  decfsz  0x4f, F                                ; reg: 0x04f
0a66:  2a5e  goto    0x025e
0a67:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a68:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0a69:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0a6a:  2bcf  goto    label_128
0a6b:  08ed  movf    0x6d, F                                ; reg: 0x06d
0a6c:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0a6d:  2a73  goto    label_115
0a6e:  084c  movf    0x4c, W                                ; reg: 0x04c
0a6f:  3970  andlw   0x70
0a70:  3c60  sublw   0x60
0a71:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0a72:  2a83  goto    label_117

label_115:                                                  ; address: 0x0a73

0a73:  1b7e  btfsc   (Common_RAM + 14), 0x6                 ; reg: 0x07e
0a74:  2a83  goto    label_117
0a75:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074

label_116:                                                  ; address: 0x0a76

0a76:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
0a77:  3c07  sublw   0x07
0a78:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0a79:  2a83  goto    label_117
0a7a:  3063  movlw   0x63
0a7b:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0a7c:  0084  movwf   FSR                                    ; reg: 0x004
0a7d:  0857  movf    0x57, W                                ; reg: 0x057
0a7e:  0080  movwf   INDF                                   ; reg: 0x000
0a7f:  0857  movf    0x57, W                                ; reg: 0x057
0a80:  00eb  movwf   0x6b                                   ; reg: 0x06b
0a81:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
0a82:  2a76  goto    label_116

label_117:                                                  ; address: 0x0a83

0a83:  084c  movf    0x4c, W                                ; reg: 0x04c
0a84:  3970  andlw   0x70
0a85:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a86:  00c8  movwf   0x48                                   ; reg: 0x048
0a87:  0848  movf    0x48, W                                ; reg: 0x048
0a88:  3c3f  sublw   0x3f
0a89:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0a8a:  2bfb  goto    label_129
0a8b:  0848  movf    0x48, W                                ; reg: 0x048
0a8c:  3c5f  sublw   0x5f
0a8d:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0a8e:  2bfb  goto    label_129
0a8f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0a90:  085a  movf    0x5a, W                                ; reg: 0x05a
0a91:  0257  subwf   0x57, W                                ; reg: 0x057
0a92:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0a93:  2a96  goto    label_118
0a94:  0857  movf    0x57, W                                ; reg: 0x057
0a95:  00da  movwf   0x5a                                   ; reg: 0x05a

label_118:                                                  ; address: 0x0a96

0a96:  0861  movf    0x61, W                                ; reg: 0x061
0a97:  3c00  sublw   0x00
0a98:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0a99:  2b43  goto    label_127
0a9a:  085a  movf    0x5a, W                                ; reg: 0x05a
0a9b:  026b  subwf   0x6b, W                                ; reg: 0x06b
0a9c:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0a9d:  2ab3  goto    label_120
0a9e:  0aeb  incf    0x6b, F                                ; reg: 0x06b
0a9f:  085a  movf    0x5a, W                                ; reg: 0x05a
0aa0:  3cc7  sublw   0xc7
0aa1:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0aa2:  2ab1  goto    label_119
0aa3:  085a  movf    0x5a, W                                ; reg: 0x05a
0aa4:  026b  subwf   0x6b, W                                ; reg: 0x06b
0aa5:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0aa6:  2ab1  goto    label_119
0aa7:  0aeb  incf    0x6b, F                                ; reg: 0x06b
0aa8:  085a  movf    0x5a, W                                ; reg: 0x05a
0aa9:  3c95  sublw   0x95
0aaa:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0aab:  2ab1  goto    label_119
0aac:  085a  movf    0x5a, W                                ; reg: 0x05a
0aad:  026b  subwf   0x6b, W                                ; reg: 0x06b
0aae:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0aaf:  2ab1  goto    label_119
0ab0:  0aeb  incf    0x6b, F                                ; reg: 0x06b

label_119:                                                  ; address: 0x0ab1

0ab1:  086b  movf    0x6b, W                                ; reg: 0x06b
0ab2:  00da  movwf   0x5a                                   ; reg: 0x05a

label_120:                                                  ; address: 0x0ab3

0ab3:  3063  movlw   0x63
0ab4:  0762  addwf   0x62, W                                ; reg: 0x062
0ab5:  0084  movwf   FSR                                    ; reg: 0x004
0ab6:  085a  movf    0x5a, W                                ; reg: 0x05a
0ab7:  0080  movwf   INDF                                   ; reg: 0x000
0ab8:  1bfe  btfsc   (Common_RAM + 14), 0x7                 ; reg: 0x07e
0ab9:  2af9  goto    label_126
0aba:  01eb  clrf    0x6b                                   ; reg: 0x06b
0abb:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
0abc:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
0abd:  3c07  sublw   0x07
0abe:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0abf:  2aee  goto    label_125
0ac0:  3063  movlw   0x63
0ac1:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0ac2:  0084  movwf   FSR                                    ; reg: 0x004
0ac3:  0800  movf    INDF, W                                ; reg: 0x000
0ac4:  025a  subwf   0x5a, W                                ; reg: 0x05a
0ac5:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0ac6:  2ace  goto    label_121
0ac7:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0ac8:  2ace  goto    label_121
0ac9:  3063  movlw   0x63
0aca:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0acb:  0084  movwf   FSR                                    ; reg: 0x004
0acc:  085a  movf    0x5a, W                                ; reg: 0x05a
0acd:  0080  movwf   INDF                                   ; reg: 0x000

label_121:                                                  ; address: 0x0ace

0ace:  3063  movlw   0x63
0acf:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0ad0:  0084  movwf   FSR                                    ; reg: 0x004
0ad1:  0800  movf    INDF, W                                ; reg: 0x000
0ad2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ad3:  00c8  movwf   0x48                                   ; reg: 0x048
0ad4:  0848  movf    0x48, W                                ; reg: 0x048
0ad5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ad6:  026b  subwf   0x6b, W                                ; reg: 0x06b
0ad7:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0ad8:  2add  goto    label_122
0ad9:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ada:  0848  movf    0x48, W                                ; reg: 0x048
0adb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0adc:  00eb  movwf   0x6b                                   ; reg: 0x06b

label_122:                                                  ; address: 0x0add

0add:  1ffe  btfss   (Common_RAM + 14), 0x7                 ; reg: 0x07e
0ade:  2ae1  goto    label_123
0adf:  3010  movlw   0x10
0ae0:  2ae2  goto    label_124

label_123:                                                  ; address: 0x0ae1

0ae1:  3018  movlw   0x18

label_124:                                                  ; address: 0x0ae2

0ae2:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0ae3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ae4:  00ca  movwf   0x4a                                   ; reg: 0x04a
0ae5:  00d3  movwf   0x53                                   ; reg: 0x053
0ae6:  0848  movf    0x48, W                                ; reg: 0x048
0ae7:  00d4  movwf   0x54                                   ; reg: 0x054
0ae8:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0ae9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0aea:  22bc  call    function_014
0aeb:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0aec:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
0aed:  2abc  goto    0x02bc

label_125:                                                  ; address: 0x0aee

0aee:  3006  movlw   0x06
0aef:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0af0:  00d3  movwf   0x53                                   ; reg: 0x053
0af1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0af2:  086b  movf    0x6b, W                                ; reg: 0x06b
0af3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0af4:  00d4  movwf   0x54                                   ; reg: 0x054
0af5:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0af6:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0af7:  22bc  call    0x02bc
0af8:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_126:                                                  ; address: 0x0af9

0af9:  1ffe  btfss   (Common_RAM + 14), 0x7                 ; reg: 0x07e
0afa:  2afd  goto    0x02fd
0afb:  3010  movlw   0x10
0afc:  2afe  goto    0x02fe
0afd:  3018  movlw   0x18
0afe:  0762  addwf   0x62, W                                ; reg: 0x062
0aff:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b00:  00ca  movwf   0x4a                                   ; reg: 0x04a
0b01:  00d3  movwf   0x53                                   ; reg: 0x053
0b02:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b03:  085a  movf    0x5a, W                                ; reg: 0x05a
0b04:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b05:  00d4  movwf   0x54                                   ; reg: 0x054
0b06:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0b07:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b08:  22bc  call    0x02bc
0b09:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0b0a:  3005  movlw   0x05
0b0b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b0c:  00d3  movwf   0x53                                   ; reg: 0x053
0b0d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b0e:  0862  movf    0x62, W                                ; reg: 0x062
0b0f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b10:  00d4  movwf   0x54                                   ; reg: 0x054
0b11:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0b12:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b13:  22bc  call    0x02bc
0b14:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0b15:  0ae2  incf    0x62, F                                ; reg: 0x062
0b16:  086b  movf    0x6b, W                                ; reg: 0x06b
0b17:  025a  subwf   0x5a, W                                ; reg: 0x05a
0b18:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0b19:  2b40  goto    0x0340
0b1a:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
0b1b:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
0b1c:  3c07  sublw   0x07
0b1d:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0b1e:  2b28  goto    0x0328
0b1f:  3063  movlw   0x63
0b20:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0b21:  0084  movwf   FSR                                    ; reg: 0x004
0b22:  086b  movf    0x6b, W                                ; reg: 0x06b
0b23:  0080  movwf   INDF                                   ; reg: 0x000
0b24:  086b  movf    0x6b, W                                ; reg: 0x06b
0b25:  00ec  movwf   0x6c                                   ; reg: 0x06c
0b26:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
0b27:  2b1b  goto    0x031b
0b28:  3018  movlw   0x18
0b29:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0b2a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b2b:  00c9  movwf   0x49                                   ; reg: 0x049
0b2c:  00d3  movwf   0x53                                   ; reg: 0x053
0b2d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b2e:  086b  movf    0x6b, W                                ; reg: 0x06b
0b2f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b30:  00d4  movwf   0x54                                   ; reg: 0x054
0b31:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0b32:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b33:  22bc  call    0x02bc
0b34:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0b35:  3006  movlw   0x06
0b36:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b37:  00d3  movwf   0x53                                   ; reg: 0x053
0b38:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b39:  086b  movf    0x6b, W                                ; reg: 0x06b
0b3a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b3b:  00d4  movwf   0x54                                   ; reg: 0x054
0b3c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0b3d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b3e:  22bc  call    0x02bc
0b3f:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0b40:  0857  movf    0x57, W                                ; reg: 0x057
0b41:  00da  movwf   0x5a                                   ; reg: 0x05a
0b42:  01e1  clrf    0x61                                   ; reg: 0x061

label_127:                                                  ; address: 0x0b43

0b43:  21d1  call    0x01d1
0b44:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0b45:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b46:  00c8  movwf   0x48                                   ; reg: 0x048
0b47:  1bfe  btfsc   (Common_RAM + 14), 0x7                 ; reg: 0x07e
0b48:  2bad  goto    0x03ad
0b49:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b4a:  01ee  clrf    0x6e                                   ; reg: 0x06e
0b4b:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
0b4c:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
0b4d:  3c07  sublw   0x07
0b4e:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0b4f:  2b9a  goto    0x039a
0b50:  086b  movf    0x6b, W                                ; reg: 0x06b
0b51:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b52:  0248  subwf   0x48, W                                ; reg: 0x048
0b53:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0b54:  2b97  goto    0x0397
0b55:  0848  movf    0x48, W                                ; reg: 0x048
0b56:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b57:  026b  subwf   0x6b, W                                ; reg: 0x06b
0b58:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b59:  00c9  movwf   0x49                                   ; reg: 0x049
0b5a:  3063  movlw   0x63
0b5b:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0b5c:  0084  movwf   FSR                                    ; reg: 0x004
0b5d:  0800  movf    INDF, W                                ; reg: 0x000
0b5e:  0249  subwf   0x49, W                                ; reg: 0x049
0b5f:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0b60:  2b68  goto    0x0368
0b61:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0b62:  2b68  goto    0x0368
0b63:  3010  movlw   0x10
0b64:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b65:  07ee  addwf   0x6e, F                                ; reg: 0x06e
0b66:  2b96  goto    0x0396
0b67:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b68:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b69:  086b  movf    0x6b, W                                ; reg: 0x06b
0b6a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b6b:  0221  subwf   0x21, W                                ; reg: 0x021
0b6c:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0b6d:  2b97  goto    0x0397
0b6e:  0821  movf    0x21, W                                ; reg: 0x021
0b6f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b70:  026b  subwf   0x6b, W                                ; reg: 0x06b
0b71:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b72:  00c9  movwf   0x49                                   ; reg: 0x049
0b73:  3063  movlw   0x63
0b74:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0b75:  0084  movwf   FSR                                    ; reg: 0x004
0b76:  0800  movf    INDF, W                                ; reg: 0x000
0b77:  0249  subwf   0x49, W                                ; reg: 0x049
0b78:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0b79:  2b8d  goto    0x038d
0b7a:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0b7b:  2b8d  goto    0x038d
0b7c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b7d:  0aee  incf    0x6e, F                                ; reg: 0x06e
0b7e:  3010  movlw   0x10
0b7f:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0b80:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b81:  00c9  movwf   0x49                                   ; reg: 0x049
0b82:  00d3  movwf   0x53                                   ; reg: 0x053
0b83:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b84:  086e  movf    0x6e, W                                ; reg: 0x06e
0b85:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b86:  00d4  movwf   0x54                                   ; reg: 0x054
0b87:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0b88:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b89:  22bc  call    0x02bc
0b8a:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0b8b:  2b96  goto    0x0396
0b8c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b8d:  3010  movlw   0x10
0b8e:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0b8f:  00c9  movwf   0x49                                   ; reg: 0x049
0b90:  00d3  movwf   0x53                                   ; reg: 0x053
0b91:  01d4  clrf    0x54                                   ; reg: 0x054
0b92:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0b93:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b94:  22bc  call    0x02bc
0b95:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0b96:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b97:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
0b98:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b99:  2b4c  goto    0x034c
0b9a:  3007  movlw   0x07
0b9b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b9c:  00d3  movwf   0x53                                   ; reg: 0x053
0b9d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0b9e:  086e  movf    0x6e, W                                ; reg: 0x06e
0b9f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ba0:  00d4  movwf   0x54                                   ; reg: 0x054
0ba1:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0ba2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ba3:  22bc  call    0x02bc
0ba4:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0ba5:  086e  movf    0x6e, W                                ; reg: 0x06e
0ba6:  3c2f  sublw   0x2f
0ba7:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0ba8:  2bab  goto    0x03ab
0ba9:  17fe  bsf     (Common_RAM + 14), 0x7                 ; reg: 0x07e
0baa:  01e2  clrf    0x62                                   ; reg: 0x062
0bab:  2bfa  goto    0x03fa
0bac:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bad:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bae:  0862  movf    0x62, W                                ; reg: 0x062
0baf:  3c07  sublw   0x07
0bb0:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0bb1:  2be6  goto    0x03e6
0bb2:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
0bb3:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
0bb4:  3c07  sublw   0x07
0bb5:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0bb6:  2bdf  goto    0x03df
0bb7:  3063  movlw   0x63
0bb8:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074

function_041:                                               ; address: 0x0bb9

0bb9:  0084  movwf   FSR                                    ; reg: 0x004
0bba:  0800  movf    INDF, W                                ; reg: 0x000
0bbb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bbc:  00c9  movwf   0x49                                   ; reg: 0x049
0bbd:  0d48  rlf     0x48, W                                ; reg: 0x048
0bbe:  00ca  movwf   0x4a                                   ; reg: 0x04a
0bbf:  0dca  rlf     0x4a, F                                ; reg: 0x04a
0bc0:  30fc  movlw   0xfc
0bc1:  05ca  andwf   0x4a, F                                ; reg: 0x04a
0bc2:  3009  movlw   0x09
0bc3:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0bc4:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0bc5:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0bc6:  0cf7  rrf     (Common_RAM + 7), F                    ; reg: 0x077
0bc7:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
0bc8:  00cc  movwf   0x4c                                   ; reg: 0x04c
0bc9:  084a  movf    0x4a, W                                ; reg: 0x04a
0bca:  00cd  movwf   0x4d                                   ; reg: 0x04d
0bcb:  084c  movf    0x4c, W                                ; reg: 0x04c
0bcc:  00ce  movwf   0x4e                                   ; reg: 0x04e
0bcd:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bce:  2a52  goto    0x0252

label_128:                                                  ; address: 0x0bcf

0bcf:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078

function_042:                                               ; address: 0x0bd0

0bd0:  026b  subwf   0x6b, W                                ; reg: 0x06b
0bd1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bd2:  0249  subwf   0x49, W                                ; reg: 0x049
0bd3:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0bd4:  2bdc  goto    0x03dc
0bd5:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0bd6:  2bdc  goto    0x03dc
0bd7:  13fe  bcf     (Common_RAM + 14), 0x7                 ; reg: 0x07e
0bd8:  137e  bcf     (Common_RAM + 14), 0x6                 ; reg: 0x07e
0bd9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bda:  1330  bcf     0x30, 0x6                              ; reg: 0x030
0bdb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bdc:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
0bdd:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bde:  2bb3  goto    0x03b3
0bdf:  1ffe  btfss   (Common_RAM + 14), 0x7                 ; reg: 0x07e
0be0:  2be5  goto    0x03e5
0be1:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
0be2:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
0be3:  177e  bsf     (Common_RAM + 14), 0x6                 ; reg: 0x07e
0be4:  1330  bcf     0x30, 0x6                              ; reg: 0x030
0be5:  2bfa  goto    0x03fa
0be6:  3063  movlw   0x63
0be7:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
0be8:  0084  movwf   FSR                                    ; reg: 0x004
0be9:  0800  movf    INDF, W                                ; reg: 0x000
0bea:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0beb:  00c9  movwf   0x49                                   ; reg: 0x049
0bec:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0bed:  0d48  rlf     0x48, W                                ; reg: 0x048
0bee:  0249  subwf   0x49, W                                ; reg: 0x049
0bef:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0bf0:  2bfb  goto    0x03fb
0bf1:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0bf2:  2bfb  goto    0x03fb
0bf3:  1ffe  btfss   (Common_RAM + 14), 0x7                 ; reg: 0x07e
0bf4:  2bfb  goto    0x03fb
0bf5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bf6:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
0bf7:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
0bf8:  177e  bsf     (Common_RAM + 14), 0x6                 ; reg: 0x07e
0bf9:  1330  bcf     0x30, 0x6                              ; reg: 0x030
0bfa:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_129:                                                  ; address: 0x0bfb

0bfb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0bfc:  0862  movf    0x62, W                                ; reg: 0x062
0bfd:  3c07  sublw   0x07
0bfe:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0bff:  2c01  goto    0x0401
0c00:  01e2  clrf    0x62                                   ; reg: 0x062
0c01:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0c02:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0c03:  2c60  goto    label_132
0c04:  1c7e  btfss   (Common_RAM + 14), 0x0                 ; reg: 0x07e
0c05:  2c12  goto    label_130
0c06:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c07:  0849  movf    0x49, W                                ; reg: 0x049
0c08:  00da  movwf   0x5a                                   ; reg: 0x05a
0c09:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0c0a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c0b:  23d0  call    function_017
0c0c:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0c0d:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0c0e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c0f:  00ca  movwf   0x4a                                   ; reg: 0x04a
0c10:  2c15  goto    0x0415
0c11:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_130:                                                  ; address: 0x0c12

0c12:  3010  movlw   0x10
0c13:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c14:  00ca  movwf   0x4a                                   ; reg: 0x04a
0c15:  084a  movf    0x4a, W                                ; reg: 0x04a
0c16:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0c17:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c18:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0c19:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
0c1a:  2c69  goto    label_133
0c1b:  1ec3  btfss   0x43, 0x5                              ; reg: 0x043
0c1c:  2c22  goto    label_131
0c1d:  1c86  btfss   PORTB, RB1                             ; reg: 0x006, bit: 1
0c1e:  2c22  goto    label_131
0c1f:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0c20:  26a9  call    function_027
0c21:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_131:                                                  ; address: 0x0c22

0c22:  1c86  btfss   PORTB, RB1                             ; reg: 0x006, bit: 1
0c23:  2c55  goto    0x0455
0c24:  1fc3  btfss   0x43, 0x7                              ; reg: 0x043
0c25:  2c43  goto    0x0443
0c26:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0c27:  26a9  call    0x06a9
0c28:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0c29:  30f0  movlw   0xf0
0c2a:  05c3  andwf   0x43, F                                ; reg: 0x043
0c2b:  0847  movf    0x47, W                                ; reg: 0x047
0c2c:  00c5  movwf   0x45                                   ; reg: 0x045
0c2d:  0846  movf    0x46, W                                ; reg: 0x046
0c2e:  00c4  movwf   0x44                                   ; reg: 0x044
0c2f:  0845  movf    0x45, W                                ; reg: 0x045
0c30:  3c13  sublw   0x13
0c31:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0c32:  2c3e  goto    0x043e
0c33:  3aff  xorlw   0xff
0c34:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0c35:  2c3a  goto    0x043a
0c36:  0844  movf    0x44, W                                ; reg: 0x044
0c37:  3c50  sublw   0x50
0c38:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0c39:  2c3e  goto    0x043e
0c3a:  3014  movlw   0x14
0c3b:  00c5  movwf   0x45                                   ; reg: 0x045
0c3c:  3050  movlw   0x50
0c3d:  00c4  movwf   0x44                                   ; reg: 0x044
0c3e:  01c7  clrf    0x47                                   ; reg: 0x047
0c3f:  01c6  clrf    0x46                                   ; reg: 0x046
0c40:  13c3  bcf     0x43, 0x7                              ; reg: 0x043
0c41:  1243  bcf     0x43, 0x4                              ; reg: 0x043
0c42:  2c54  goto    0x0454
0c43:  08f1  movf    (Common_RAM + 1), F                    ; reg: 0x071
0c44:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0c45:  2c54  goto    0x0454
0c46:  08f2  movf    (Common_RAM + 2), F                    ; reg: 0x072
0c47:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0c48:  2c54  goto    0x0454
0c49:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0c4a:  26a9  call    0x06a9
0c4b:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0c4c:  0843  movf    0x43, W                                ; reg: 0x043
0c4d:  390f  andlw   0x0f
0c4e:  3c06  sublw   0x06
0c4f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0c50:  2c53  goto    0x0453
0c51:  0ac3  incf    0x43, F                                ; reg: 0x043
0c52:  2c54  goto    0x0454
0c53:  17cf  bsf     0x4f, 0x7                              ; reg: 0x04f
0c54:  2cc0  goto    0x04c0
0c55:  08f1  movf    (Common_RAM + 1), F                    ; reg: 0x071
0c56:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0c57:  2cc0  goto    0x04c0
0c58:  08f2  movf    (Common_RAM + 2), F                    ; reg: 0x072
0c59:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0c5a:  2cc0  goto    0x04c0
0c5b:  19cf  btfsc   0x4f, 0x3                              ; reg: 0x04f
0c5c:  2cc0  goto    0x04c0
0c5d:  1ac3  btfsc   0x43, 0x5                              ; reg: 0x043
0c5e:  2cc0  goto    0x04c0
0c5f:  2a6b  goto    0x026b

label_132:                                                  ; address: 0x0c60

0c60:  1486  bsf     PORTB, RB1                             ; reg: 0x006, bit: 1
0c61:  084c  movf    0x4c, W                                ; reg: 0x04c
0c62:  3907  andlw   0x07
0c63:  3e50  addlw   0x50
0c64:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c65:  00c8  movwf   0x48                                   ; reg: 0x048
0c66:  00c9  movwf   0x49                                   ; reg: 0x049
0c67:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c68:  2c04  goto    0x0404

label_133:                                                  ; address: 0x0c69

0c69:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0c6a:  07b9  addwf   0x39, F                                ; reg: 0x039
0c6b:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0c6c:  0aba  incf    0x3a, F                                ; reg: 0x03a
0c6d:  2113  call    0x0113
0c6e:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0c6f:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
0c70:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
0c71:  023a  subwf   0x3a, W                                ; reg: 0x03a
0c72:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0c73:  2c82  goto    0x0482
0c74:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0c75:  2c7a  goto    0x047a
0c76:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0c77:  0239  subwf   0x39, W                                ; reg: 0x039
0c78:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0c79:  2c82  goto    0x0482
0c7a:  14d0  bsf     0x50, 0x1                              ; reg: 0x050
0c7b:  2113  call    0x0113
0c7c:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0c7d:  02b9  subwf   0x39, F                                ; reg: 0x039
0c7e:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0c7f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0c80:  0f79  incfsz  (Common_RAM + 9), W                    ; reg: 0x079
0c81:  02ba  subwf   0x3a, F                                ; reg: 0x03a
0c82:  0ae1  incf    0x61, F                                ; reg: 0x061
0c83:  08c5  movf    0x45, F                                ; reg: 0x045
0c84:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0c85:  2c8e  goto    0x048e
0c86:  0844  movf    0x44, W                                ; reg: 0x044
0c87:  3c63  sublw   0x63
0c88:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0c89:  2c8e  goto    0x048e
0c8a:  3002  movlw   0x02
0c8b:  00c5  movwf   0x45                                   ; reg: 0x045
0c8c:  308a  movlw   0x8a
0c8d:  00c4  movwf   0x44                                   ; reg: 0x044
0c8e:  1b43  btfsc   0x43, 0x6                              ; reg: 0x043
0c8f:  2cab  goto    0x04ab
0c90:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
0c91:  0d44  rlf     0x44, W                                ; reg: 0x044
0c92:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c93:  00c8  movwf   0x48                                   ; reg: 0x048
0c94:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c95:  0d45  rlf     0x45, W                                ; reg: 0x045
0c96:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c97:  00c9  movwf   0x49                                   ; reg: 0x049
0c98:  0849  movf    0x49, W                                ; reg: 0x049
0c99:  00d1  movwf   0x51                                   ; reg: 0x051
0c9a:  0848  movf    0x48, W                                ; reg: 0x048
0c9b:  00d0  movwf   0x50                                   ; reg: 0x050
0c9c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0c9d:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6
0c9e:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
0c9f:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
0ca0:  2c9e  goto    0x049e
0ca1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ca2:  0851  movf    0x51, W                                ; reg: 0x051
0ca3:  00f2  movwf   (Common_RAM + 2)                       ; reg: 0x072
0ca4:  0850  movf    0x50, W                                ; reg: 0x050
0ca5:  00f1  movwf   (Common_RAM + 1)                       ; reg: 0x071
0ca6:  30c0  movlw   0xc0
0ca7:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ca8:  048b  iorwf   INTCON, F                              ; reg: 0x00b
0ca9:  1343  bcf     0x43, 0x6                              ; reg: 0x043
0caa:  2cc0  goto    0x04c0
0cab:  0845  movf    0x45, W                                ; reg: 0x045
0cac:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cad:  00d1  movwf   0x51                                   ; reg: 0x051
0cae:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0caf:  0844  movf    0x44, W                                ; reg: 0x044
0cb0:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cb1:  00d0  movwf   0x50                                   ; reg: 0x050
0cb2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cb3:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6
0cb4:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
0cb5:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
0cb6:  2cb4  goto    0x04b4
0cb7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cb8:  0851  movf    0x51, W                                ; reg: 0x051
0cb9:  00f2  movwf   (Common_RAM + 2)                       ; reg: 0x072
0cba:  0850  movf    0x50, W                                ; reg: 0x050
0cbb:  00f1  movwf   (Common_RAM + 1)                       ; reg: 0x071
0cbc:  30c0  movlw   0xc0
0cbd:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cbe:  048b  iorwf   INTCON, F                              ; reg: 0x00b
0cbf:  1343  bcf     0x43, 0x6                              ; reg: 0x043
0cc0:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0cc1:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
0cc2:  289e  goto    label_238

function_043:                                               ; address: 0x0cc3

0cc3:  083b  movf    0x3b, W                                ; reg: 0x03b
0cc4:  390f  andlw   0x0f
0cc5:  3c0c  sublw   0x0c
0cc6:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0cc7:  2cc9  goto    label_339
0cc8:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
0cc9:  1030  bcf     0x30, 0x0                              ; reg: 0x030
0cca:  1a08  btfsc   PORTD, RD4                             ; reg: 0x008, bit: 4
0ccb:  1430  bsf     0x30, 0x0                              ; reg: 0x030
0ccc:  1a08  btfsc   PORTD, RD4                             ; reg: 0x008, bit: 4
0ccd:  2cd0  goto    label_341
0cce:  01de  clrf    0x5e                                   ; reg: 0x05e
0ccf:  2cda  goto    label_342
0cd0:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0cd1:  27ef  call    function_060
0cd2:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0cd3:  300c  movlw   0x0c
0cd4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cd5:  00d4  movwf   0x54                                   ; reg: 0x054
0cd6:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0cd7:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cd8:  2760  call    0x0760
0cd9:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0cda:  085e  movf    0x5e, W                                ; reg: 0x05e
0cdb:  3ce0  sublw   0xe0
0cdc:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0cdd:  2ce1  goto    0x04e1
0cde:  164f  bsf     0x4f, 0x4                              ; reg: 0x04f
0cdf:  30e1  movlw   0xe1
0ce0:  00de  movwf   0x5e                                   ; reg: 0x05e
0ce1:  1c88  btfss   PORTD, RD1                             ; reg: 0x008, bit: 1
0ce2:  2cef  goto    0x04ef
0ce3:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0ce4:  27ef  call    0x07ef
0ce5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0ce6:  15cf  bsf     0x4f, 0x3                              ; reg: 0x04f
0ce7:  3018  movlw   0x18
0ce8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ce9:  00d4  movwf   0x54                                   ; reg: 0x054
0cea:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0ceb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0cec:  2760  call    0x0760
0ced:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0cee:  2cf6  goto    0x04f6
0cef:  085f  movf    0x5f, W                                ; reg: 0x05f
0cf0:  3cb3  sublw   0xb3
0cf1:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0cf2:  2cf6  goto    0x04f6
0cf3:  1130  bcf     0x30, 0x2                              ; reg: 0x030
0cf4:  11cf  bcf     0x4f, 0x3                              ; reg: 0x04f
0cf5:  01df  clrf    0x5f                                   ; reg: 0x05f
0cf6:  085f  movf    0x5f, W                                ; reg: 0x05f
0cf7:  3cb3  sublw   0xb3
0cf8:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0cf9:  2cfe  goto    0x04fe
0cfa:  1530  bsf     0x30, 0x2                              ; reg: 0x030
0cfb:  15cf  bsf     0x4f, 0x3                              ; reg: 0x04f
0cfc:  30b4  movlw   0xb4
0cfd:  00df  movwf   0x5f                                   ; reg: 0x05f
0cfe:  1f4f  btfss   0x4f, 0x6                              ; reg: 0x04f
0cff:  2d01  goto    0x0501
0d00:  15b0  bsf     0x30, 0x3                              ; reg: 0x030
0d01:  3400  retlw   0x00
0d02:  1c7e  btfss   (Common_RAM + 14), 0x0                 ; reg: 0x07e
0d03:  2d2a  goto    0x052a
0d04:  3068  movlw   0x68
0d05:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d06:  00cc  movwf   0x4c                                   ; reg: 0x04c
0d07:  084c  movf    0x4c, W                                ; reg: 0x04c
0d08:  00da  movwf   0x5a                                   ; reg: 0x05a
0d09:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0d0a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d0b:  23d0  call    0x03d0
0d0c:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0d0d:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0d0e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d0f:  00ca  movwf   0x4a                                   ; reg: 0x04a
0d10:  0acc  incf    0x4c, F                                ; reg: 0x04c
0d11:  084c  movf    0x4c, W                                ; reg: 0x04c
0d12:  00da  movwf   0x5a                                   ; reg: 0x05a
0d13:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0d14:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d15:  23d0  call    0x03d0
0d16:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0d17:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0d18:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d19:  00cb  movwf   0x4b                                   ; reg: 0x04b
0d1a:  084a  movf    0x4a, W                                ; reg: 0x04a
0d1b:  3c82  sublw   0x82
0d1c:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0d1d:  2d20  goto    0x0520
0d1e:  3082  movlw   0x82
0d1f:  00ca  movwf   0x4a                                   ; reg: 0x04a
0d20:  3028  movlw   0x28
0d21:  074a  addwf   0x4a, W                                ; reg: 0x04a
0d22:  024b  subwf   0x4b, W                                ; reg: 0x04b
0d23:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0d24:  2d28  goto    0x0528
0d25:  3028  movlw   0x28
0d26:  074a  addwf   0x4a, W                                ; reg: 0x04a
0d27:  00cb  movwf   0x4b                                   ; reg: 0x04b
0d28:  2d2f  goto    0x052f
0d29:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d2a:  305a  movlw   0x5a
0d2b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d2c:  00ca  movwf   0x4a                                   ; reg: 0x04a
0d2d:  30aa  movlw   0xaa
0d2e:  00cb  movwf   0x4b                                   ; reg: 0x04b
0d2f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d30:  19d1  btfsc   0x51, 0x3                              ; reg: 0x051
0d31:  2da3  goto    0x05a3
0d32:  0857  movf    0x57, W                                ; reg: 0x057
0d33:  3c13  sublw   0x13
0d34:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0d35:  2d47  goto    0x0547
0d36:  01a9  clrf    0x29                                   ; reg: 0x029
0d37:  084c  movf    0x4c, W                                ; reg: 0x04c
0d38:  3970  andlw   0x70
0d39:  3c20  sublw   0x20
0d3a:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0d3b:  2d46  goto    0x0546
0d3c:  084c  movf    0x4c, W                                ; reg: 0x04c
0d3d:  3907  andlw   0x07
0d3e:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
0d3f:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
0d40:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
0d41:  30fc  movlw   0xfc
0d42:  05f7  andwf   (Common_RAM + 7), F                    ; reg: 0x077
0d43:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
0d44:  3e19  addlw   0x19
0d45:  00a9  movwf   0x29                                   ; reg: 0x029
0d46:  2da3  goto    0x05a3
0d47:  0857  movf    0x57, W                                ; reg: 0x057
0d48:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d49:  024a  subwf   0x4a, W                                ; reg: 0x04a
0d4a:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0d4b:  2d51  goto    0x0551
0d4c:  3019  movlw   0x19
0d4d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d4e:  00a9  movwf   0x29                                   ; reg: 0x029
0d4f:  2d9d  goto    0x059d
0d50:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d51:  084b  movf    0x4b, W                                ; reg: 0x04b
0d52:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d53:  0257  subwf   0x57, W                                ; reg: 0x057
0d54:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0d55:  2d59  goto    0x0559
0d56:  3064  movlw   0x64
0d57:  00a9  movwf   0x29                                   ; reg: 0x029
0d58:  2d9d  goto    0x059d
0d59:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d5a:  084a  movf    0x4a, W                                ; reg: 0x04a
0d5b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d5c:  0257  subwf   0x57, W                                ; reg: 0x057
0d5d:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
0d5e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d5f:  00cd  movwf   0x4d                                   ; reg: 0x04d
0d60:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
0d61:  00ce  movwf   0x4e                                   ; reg: 0x04e
0d62:  01d7  clrf    0x57                                   ; reg: 0x057
0d63:  304b  movlw   0x4b
0d64:  00d6  movwf   0x56                                   ; reg: 0x056
0d65:  084e  movf    0x4e, W                                ; reg: 0x04e
0d66:  00d9  movwf   0x59                                   ; reg: 0x059
0d67:  084d  movf    0x4d, W                                ; reg: 0x04d
0d68:  00d8  movwf   0x58                                   ; reg: 0x058
0d69:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0d6a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d6b:  23b9  call    0x03b9
0d6c:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0d6d:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0d6e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d6f:  00cf  movwf   0x4f                                   ; reg: 0x04f
0d70:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0d71:  00ce  movwf   0x4e                                   ; reg: 0x04e
0d72:  084a  movf    0x4a, W                                ; reg: 0x04a
0d73:  024b  subwf   0x4b, W                                ; reg: 0x04b
0d74:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
0d75:  00d0  movwf   0x50                                   ; reg: 0x050
0d76:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
0d77:  00d1  movwf   0x51                                   ; reg: 0x051
0d78:  084f  movf    0x4f, W                                ; reg: 0x04f
0d79:  00d5  movwf   0x55                                   ; reg: 0x055
0d7a:  084e  movf    0x4e, W                                ; reg: 0x04e
0d7b:  00d4  movwf   0x54                                   ; reg: 0x054
0d7c:  0851  movf    0x51, W                                ; reg: 0x051
0d7d:  00d7  movwf   0x57                                   ; reg: 0x057
0d7e:  0850  movf    0x50, W                                ; reg: 0x050
0d7f:  00d6  movwf   0x56                                   ; reg: 0x056
0d80:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0d81:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d82:  24a2  call    0x04a2
0d83:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0d84:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0d85:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d86:  00d0  movwf   0x50                                   ; reg: 0x050
0d87:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0d88:  00cf  movwf   0x4f                                   ; reg: 0x04f
0d89:  3019  movlw   0x19
0d8a:  074f  addwf   0x4f, W                                ; reg: 0x04f
0d8b:  00c8  movwf   0x48                                   ; reg: 0x048
0d8c:  0850  movf    0x50, W                                ; reg: 0x050
0d8d:  00c9  movwf   0x49                                   ; reg: 0x049
0d8e:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0d8f:  0ac9  incf    0x49, F                                ; reg: 0x049
0d90:  08c9  movf    0x49, F                                ; reg: 0x049
0d91:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0d92:  2d97  goto    0x0597
0d93:  0848  movf    0x48, W                                ; reg: 0x048
0d94:  3c64  sublw   0x64
0d95:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0d96:  2d9a  goto    0x059a
0d97:  01c9  clrf    0x49                                   ; reg: 0x049
0d98:  3064  movlw   0x64
0d99:  00c8  movwf   0x48                                   ; reg: 0x048
0d9a:  0848  movf    0x48, W                                ; reg: 0x048
0d9b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0d9c:  00a9  movwf   0x29                                   ; reg: 0x029
0d9d:  0829  movf    0x29, W                                ; reg: 0x029
0d9e:  3c18  sublw   0x18
0d9f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0da0:  2da3  goto    0x05a3
0da1:  3019  movlw   0x19
0da2:  00a9  movwf   0x29                                   ; reg: 0x029
0da3:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0da4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
0da5:  28a4  goto    label_239

label_134:                                                  ; address: 0x0da6

0da6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0da7:  0820  movf    0x20, W                                ; reg: 0x020
0da8:  00ca  movwf   0x4a                                   ; reg: 0x04a
0da9:  104b  bcf     0x4b, 0x0                              ; reg: 0x04b
0daa:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dab:  19d1  btfsc   0x51, 0x3                              ; reg: 0x051
0dac:  2f24  goto    0x0724
0dad:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dae:  08a0  movf    0x20, F                                ; reg: 0x020
0daf:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0db0:  2db6  goto    label_345
0db1:  0822  movf    0x22, W                                ; reg: 0x022
0db2:  00c8  movwf   0x48                                   ; reg: 0x048
0db3:  01c9  clrf    0x49                                   ; reg: 0x049
0db4:  1bfe  btfsc   (Common_RAM + 14), 0x7                 ; reg: 0x07e
0db5:  0ac9  incf    0x49, F                                ; reg: 0x049
0db6:  0b20  decfsz  0x20, W                                ; reg: 0x020
0db7:  2dbf  goto    label_347
0db8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0db9:  0857  movf    0x57, W                                ; reg: 0x057
0dba:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dbb:  00c8  movwf   0x48                                   ; reg: 0x048
0dbc:  01c9  clrf    0x49                                   ; reg: 0x049
0dbd:  1b7e  btfsc   (Common_RAM + 14), 0x6                 ; reg: 0x07e
0dbe:  0ac9  incf    0x49, F                                ; reg: 0x049
0dbf:  0820  movf    0x20, W                                ; reg: 0x020
0dc0:  3c02  sublw   0x02
0dc1:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0dc2:  2dcf  goto    label_349
0dc3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dc4:  082e  movf    0x2e, W                                ; reg: 0x02e
0dc5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dc6:  00c8  movwf   0x48                                   ; reg: 0x048
0dc7:  01c9  clrf    0x49                                   ; reg: 0x049
0dc8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dc9:  1f30  btfss   0x30, 0x6                              ; reg: 0x030
0dca:  2dce  goto    label_348
0dcb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dcc:  0ac9  incf    0x49, F                                ; reg: 0x049
0dcd:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dce:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dcf:  0820  movf    0x20, W                                ; reg: 0x020
0dd0:  3c03  sublw   0x03
0dd1:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0dd2:  2dd8  goto    label_351
0dd3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dd4:  082f  movf    0x2f, W                                ; reg: 0x02f
0dd5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dd6:  00c8  movwf   0x48                                   ; reg: 0x048
0dd7:  01c9  clrf    0x49                                   ; reg: 0x049
0dd8:  0820  movf    0x20, W                                ; reg: 0x020
0dd9:  3c04  sublw   0x04
0dda:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0ddb:  2de8  goto    label_353
0ddc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ddd:  0834  movf    0x34, W                                ; reg: 0x034
0dde:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ddf:  00c8  movwf   0x48                                   ; reg: 0x048
0de0:  01c9  clrf    0x49                                   ; reg: 0x049
0de1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0de2:  1c50  btfss   0x50, 0x0                              ; reg: 0x050
0de3:  2de7  goto    label_352
0de4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0de5:  0ac9  incf    0x49, F                                ; reg: 0x049
0de6:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0de7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0de8:  0820  movf    0x20, W                                ; reg: 0x020
0de9:  3c05  sublw   0x05
0dea:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0deb:  2df4  goto    label_354
0dec:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ded:  0837  movf    0x37, W                                ; reg: 0x037
0dee:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0def:  00c8  movwf   0x48                                   ; reg: 0x048
0df0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0df1:  0862  movf    0x62, W                                ; reg: 0x062
0df2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0df3:  00c9  movwf   0x49                                   ; reg: 0x049
0df4:  0820  movf    0x20, W                                ; reg: 0x020
0df5:  3c06  sublw   0x06
0df6:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0df7:  2e00  goto    label_355
0df8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0df9:  0829  movf    0x29, W                                ; reg: 0x029
0dfa:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dfb:  00c8  movwf   0x48                                   ; reg: 0x048
0dfc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dfd:  086b  movf    0x6b, W                                ; reg: 0x06b
0dfe:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0dff:  00c9  movwf   0x49                                   ; reg: 0x049
0e00:  0820  movf    0x20, W                                ; reg: 0x020
0e01:  3c07  sublw   0x07
0e02:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e03:  2e09  goto    label_356
0e04:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e05:  0848  movf    0x48, W                                ; reg: 0x048
0e06:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e07:  00c8  movwf   0x48                                   ; reg: 0x048
0e08:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0e09:  0820  movf    0x20, W                                ; reg: 0x020
0e0a:  3c08  sublw   0x08
0e0b:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e0c:  2e15  goto    label_359
0e0d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e0e:  082d  movf    0x2d, W                                ; reg: 0x02d
0e0f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e10:  00c8  movwf   0x48                                   ; reg: 0x048
0e11:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e12:  086c  movf    0x6c, W                                ; reg: 0x06c
0e13:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e14:  00c9  movwf   0x49                                   ; reg: 0x049
0e15:  0820  movf    0x20, W                                ; reg: 0x020
0e16:  3c09  sublw   0x09
0e17:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e18:  2e1e  goto    label_360
0e19:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e1a:  084c  movf    0x4c, W                                ; reg: 0x04c
0e1b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e1c:  00c8  movwf   0x48                                   ; reg: 0x048
0e1d:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0e1e:  0820  movf    0x20, W                                ; reg: 0x020
0e1f:  3c0a  sublw   0x0a
0e20:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e21:  2e27  goto    label_362
0e22:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e23:  083a  movf    0x3a, W                                ; reg: 0x03a
0e24:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e25:  00c8  movwf   0x48                                   ; reg: 0x048
0e26:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0e27:  0820  movf    0x20, W                                ; reg: 0x020
0e28:  3c0b  sublw   0x0b
0e29:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e2a:  2e30  goto    label_364
0e2b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e2c:  0839  movf    0x39, W                                ; reg: 0x039
0e2d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e2e:  00c8  movwf   0x48                                   ; reg: 0x048
0e2f:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0e30:  0820  movf    0x20, W                                ; reg: 0x020
0e31:  3c0c  sublw   0x0c
0e32:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e33:  2e41  goto    label_368
0e34:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e35:  2113  call    function_062
0e36:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0e37:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e38:  00cd  movwf   0x4d                                   ; reg: 0x04d
0e39:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0e3a:  00cc  movwf   0x4c                                   ; reg: 0x04c
0e3b:  084d  movf    0x4d, W                                ; reg: 0x04d
0e3c:  00c8  movwf   0x48                                   ; reg: 0x048
0e3d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e3e:  086d  movf    0x6d, W                                ; reg: 0x06d
0e3f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e40:  00c9  movwf   0x49                                   ; reg: 0x049
0e41:  0820  movf    0x20, W                                ; reg: 0x020
0e42:  3c0d  sublw   0x0d
0e43:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e44:  2e4b  goto    0x064b
0e45:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e46:  2113  call    0x0113
0e47:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0e48:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e49:  00c8  movwf   0x48                                   ; reg: 0x048
0e4a:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0e4b:  0820  movf    0x20, W                                ; reg: 0x020
0e4c:  3c0e  sublw   0x0e
0e4d:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e4e:  2e54  goto    0x0654
0e4f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e50:  0845  movf    0x45, W                                ; reg: 0x045
0e51:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e52:  00c8  movwf   0x48                                   ; reg: 0x048
0e53:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0e54:  0820  movf    0x20, W                                ; reg: 0x020
0e55:  3c0f  sublw   0x0f
0e56:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e57:  2e60  goto    0x0660
0e58:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e59:  0844  movf    0x44, W                                ; reg: 0x044
0e5a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e5b:  00c8  movwf   0x48                                   ; reg: 0x048
0e5c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e5d:  0860  movf    0x60, W                                ; reg: 0x060
0e5e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e5f:  00c9  movwf   0x49                                   ; reg: 0x049
0e60:  0820  movf    0x20, W                                ; reg: 0x020
0e61:  3c0f  sublw   0x0f
0e62:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0e63:  2e68  goto    0x0668
0e64:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e65:  083e  movf    0x3e, W                                ; reg: 0x03e
0e66:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e67:  00c8  movwf   0x48                                   ; reg: 0x048
0e68:  0820  movf    0x20, W                                ; reg: 0x020
0e69:  3c11  sublw   0x11
0e6a:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e6b:  2e70  goto    0x0670
0e6c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e6d:  083d  movf    0x3d, W                                ; reg: 0x03d
0e6e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e6f:  00c8  movwf   0x48                                   ; reg: 0x048
0e70:  0820  movf    0x20, W                                ; reg: 0x020
0e71:  3c12  sublw   0x12
0e72:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e73:  2e76  goto    0x0676
0e74:  087e  movf    (Common_RAM + 14), W                   ; reg: 0x07e
0e75:  00c8  movwf   0x48                                   ; reg: 0x048
0e76:  0820  movf    0x20, W                                ; reg: 0x020
0e77:  3c13  sublw   0x13
0e78:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e79:  2e7e  goto    0x067e
0e7a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e7b:  084f  movf    0x4f, W                                ; reg: 0x04f
0e7c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e7d:  00c8  movwf   0x48                                   ; reg: 0x048
0e7e:  0820  movf    0x20, W                                ; reg: 0x020
0e7f:  3c14  sublw   0x14
0e80:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e81:  2e86  goto    0x0686
0e82:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e83:  085d  movf    0x5d, W                                ; reg: 0x05d
0e84:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e85:  00c8  movwf   0x48                                   ; reg: 0x048
0e86:  0820  movf    0x20, W                                ; reg: 0x020
0e87:  3c15  sublw   0x15
0e88:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e89:  2e8e  goto    0x068e
0e8a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e8b:  0858  movf    0x58, W                                ; reg: 0x058
0e8c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e8d:  00c8  movwf   0x48                                   ; reg: 0x048
0e8e:  0820  movf    0x20, W                                ; reg: 0x020
0e8f:  3c16  sublw   0x16
0e90:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e91:  2e96  goto    0x0696
0e92:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e93:  085f  movf    0x5f, W                                ; reg: 0x05f
0e94:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e95:  00c8  movwf   0x48                                   ; reg: 0x048
0e96:  0820  movf    0x20, W                                ; reg: 0x020
0e97:  3c17  sublw   0x17
0e98:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0e99:  2e9e  goto    0x069e
0e9a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e9b:  085e  movf    0x5e, W                                ; reg: 0x05e
0e9c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0e9d:  00c8  movwf   0x48                                   ; reg: 0x048
0e9e:  0820  movf    0x20, W                                ; reg: 0x020
0e9f:  3c18  sublw   0x18
0ea0:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0ea1:  2ea7  goto    0x06a7
0ea2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ea3:  0833  movf    0x33, W                                ; reg: 0x033
0ea4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ea5:  00c8  movwf   0x48                                   ; reg: 0x048
0ea6:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0ea7:  0820  movf    0x20, W                                ; reg: 0x020
0ea8:  3c19  sublw   0x19
0ea9:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0eaa:  2eb1  goto    0x06b1
0eab:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0eac:  21d1  call    0x01d1
0ead:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0eae:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0eaf:  00c8  movwf   0x48                                   ; reg: 0x048
0eb0:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0eb1:  0820  movf    0x20, W                                ; reg: 0x020
0eb2:  3c1a  sublw   0x1a
0eb3:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0eb4:  2eb8  goto    0x06b8
0eb5:  0847  movf    0x47, W                                ; reg: 0x047
0eb6:  00c8  movwf   0x48                                   ; reg: 0x048
0eb7:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0eb8:  0820  movf    0x20, W                                ; reg: 0x020
0eb9:  3c1b  sublw   0x1b
0eba:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0ebb:  2ebf  goto    0x06bf
0ebc:  0846  movf    0x46, W                                ; reg: 0x046
0ebd:  00c8  movwf   0x48                                   ; reg: 0x048
0ebe:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0ebf:  0820  movf    0x20, W                                ; reg: 0x020
0ec0:  3c1c  sublw   0x1c
0ec1:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0ec2:  2ec8  goto    0x06c8
0ec3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ec4:  0840  movf    0x40, W                                ; reg: 0x040
0ec5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ec6:  00c8  movwf   0x48                                   ; reg: 0x048
0ec7:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0ec8:  0820  movf    0x20, W                                ; reg: 0x020
0ec9:  3c1d  sublw   0x1d
0eca:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0ecb:  2ed1  goto    0x06d1
0ecc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ecd:  083f  movf    0x3f, W                                ; reg: 0x03f
0ece:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ecf:  00c8  movwf   0x48                                   ; reg: 0x048
0ed0:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0ed1:  0820  movf    0x20, W                                ; reg: 0x020
0ed2:  3c1e  sublw   0x1e
0ed3:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0ed4:  2f00  goto    0x0700
0ed5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ed6:  21d1  call    0x01d1
0ed7:  0d78  rlf     (Common_RAM + 8), W                    ; reg: 0x078
0ed8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ed9:  00cd  movwf   0x4d                                   ; reg: 0x04d
0eda:  0dcd  rlf     0x4d, F                                ; reg: 0x04d
0edb:  30fc  movlw   0xfc
0edc:  05cd  andwf   0x4d, F                                ; reg: 0x04d
0edd:  306b  movlw   0x6b
0ede:  00da  movwf   0x5a                                   ; reg: 0x05a
0edf:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0ee0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ee1:  23d0  call    0x03d0
0ee2:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0ee3:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0ee4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ee5:  00ce  movwf   0x4e                                   ; reg: 0x04e
0ee6:  01db  clrf    0x5b                                   ; reg: 0x05b
0ee7:  084d  movf    0x4d, W                                ; reg: 0x04d
0ee8:  00da  movwf   0x5a                                   ; reg: 0x05a
0ee9:  01dd  clrf    0x5d                                   ; reg: 0x05d
0eea:  084e  movf    0x4e, W                                ; reg: 0x04e
0eeb:  00dc  movwf   0x5c                                   ; reg: 0x05c
0eec:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0eed:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0eee:  23e7  call    0x03e7
0eef:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0ef0:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0ef1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0ef2:  00cf  movwf   0x4f                                   ; reg: 0x04f
0ef3:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0ef4:  00ce  movwf   0x4e                                   ; reg: 0x04e
0ef5:  0c4f  rrf     0x4f, W                                ; reg: 0x04f
0ef6:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
0ef7:  0c4e  rrf     0x4e, W                                ; reg: 0x04e
0ef8:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
0ef9:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
0efa:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
0efb:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
0efc:  00a1  movwf   0x21                                   ; reg: 0x021
0efd:  0821  movf    0x21, W                                ; reg: 0x021
0efe:  00c8  movwf   0x48                                   ; reg: 0x048
0eff:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0f00:  0820  movf    0x20, W                                ; reg: 0x020
0f01:  3c0f  sublw   0x0f
0f02:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0f03:  2f09  goto    0x0709
0f04:  0820  movf    0x20, W                                ; reg: 0x020
0f05:  3c17  sublw   0x17
0f06:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0f07:  2f09  goto    0x0709
0f08:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
0f09:  184b  btfsc   0x4b, 0x0                              ; reg: 0x04b
0f0a:  2f14  goto    0x0714
0f0b:  084a  movf    0x4a, W                                ; reg: 0x04a
0f0c:  00d3  movwf   0x53                                   ; reg: 0x053
0f0d:  0849  movf    0x49, W                                ; reg: 0x049
0f0e:  00d4  movwf   0x54                                   ; reg: 0x054
0f0f:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0f10:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f11:  22bc  call    0x02bc
0f12:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0f13:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f14:  0820  movf    0x20, W                                ; reg: 0x020
0f15:  00d4  movwf   0x54                                   ; reg: 0x054
0f16:  0848  movf    0x48, W                                ; reg: 0x048
0f17:  00d5  movwf   0x55                                   ; reg: 0x055
0f18:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0f19:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f1a:  2771  call    0x0771
0f1b:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0f1c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f1d:  0aa0  incf    0x20, F                                ; reg: 0x020
0f1e:  0820  movf    0x20, W                                ; reg: 0x020
0f1f:  3c1e  sublw   0x1e
0f20:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0f21:  2f23  goto    0x0723
0f22:  01a0  clrf    0x20                                   ; reg: 0x020
0f23:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f24:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0f25:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
0f26:  28bb  goto    label_240

label_135:                                                  ; address: 0x0f27

0f27:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f28:  0840  movf    0x40, W                                ; reg: 0x040
0f29:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0f2a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f2b:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0f2c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
0f2d:  28c2  goto    label_242

function_044:                                               ; address: 0x0f2e


; >>> RE NOTES @ 0x0F2E
; COMMAND BUFFER GET-CHAR routine. Pulls the next byte from RAM buffer 0xA3.. and advances/decrements receive accounting.
; <<<
0f2e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f2f:  01d1  clrf    0x51                                   ; reg: 0x051
0f30:  08c0  movf    0x40, F                                ; reg: 0x040
0f31:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0f32:  2f39  goto    0x0739
0f33:  0fd1  incfsz  0x51, F                                ; reg: 0x051
0f34:  2f38  goto    0x0738
0f35:  3000  movlw   0x00
0f36:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0f37:  2f5e  goto    0x075e
0f38:  2f30  goto    0x0730
0f39:  08c0  movf    0x40, F                                ; reg: 0x040
0f3a:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
0f3b:  2f5b  goto    0x075b
0f3c:  0840  movf    0x40, W                                ; reg: 0x040
0f3d:  0241  subwf   0x41, W                                ; reg: 0x041
0f3e:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0f3f:  2f43  goto    0x0743
0f40:  0840  movf    0x40, W                                ; reg: 0x040
0f41:  0241  subwf   0x41, W                                ; reg: 0x041
0f42:  00d2  movwf   0x52                                   ; reg: 0x052
0f43:  0841  movf    0x41, W                                ; reg: 0x041
0f44:  0240  subwf   0x40, W                                ; reg: 0x040
0f45:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0f46:  2f47  goto    0x0747
0f47:  0840  movf    0x40, W                                ; reg: 0x040
0f48:  0241  subwf   0x41, W                                ; reg: 0x041
0f49:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0f4a:  2f4f  goto    0x074f
0f4b:  0840  movf    0x40, W                                ; reg: 0x040
0f4c:  3c1d  sublw   0x1d
0f4d:  0741  addwf   0x41, W                                ; reg: 0x041
0f4e:  00d2  movwf   0x52                                   ; reg: 0x052
0f4f:  0852  movf    0x52, W                                ; reg: 0x052
0f50:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0f51:  30a3  movlw   0xa3
0f52:  0778  addwf   (Common_RAM + 8), W                    ; reg: 0x078
0f53:  0084  movwf   FSR                                    ; reg: 0x004
0f54:  0800  movf    INDF, W                                ; reg: 0x000
0f55:  00d1  movwf   0x51                                   ; reg: 0x051
0f56:  03c0  decf    0x40, F                                ; reg: 0x040
0f57:  0851  movf    0x51, W                                ; reg: 0x051
0f58:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0f59:  2f5e  goto    0x075e
0f5a:  2f5e  goto    0x075e
0f5b:  3000  movlw   0x00
0f5c:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0f5d:  2f5e  goto    0x075e
0f5e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f5f:  3400  retlw   0x00

; >>> RE NOTES @ 0x0F60
; ASCII HEX digit decoder helper: converts 0-9/A-F into a nibble.
; <<<
0f60:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f61:  0851  movf    0x51, W                                ; reg: 0x051
0f62:  3c2f  sublw   0x2f
0f63:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0f64:  2f6c  goto    0x076c
0f65:  0851  movf    0x51, W                                ; reg: 0x051
0f66:  3c39  sublw   0x39
0f67:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0f68:  2f6c  goto    0x076c
0f69:  3030  movlw   0x30
0f6a:  0251  subwf   0x51, W                                ; reg: 0x051
0f6b:  00d2  movwf   0x52                                   ; reg: 0x052
0f6c:  0851  movf    0x51, W                                ; reg: 0x051
0f6d:  3c40  sublw   0x40
0f6e:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0f6f:  2f78  goto    0x0778
0f70:  0851  movf    0x51, W                                ; reg: 0x051
0f71:  3c46  sublw   0x46
0f72:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0f73:  2f78  goto    0x0778
0f74:  3041  movlw   0x41
0f75:  0251  subwf   0x51, W                                ; reg: 0x051
0f76:  3e0a  addlw   0x0a
0f77:  00d2  movwf   0x52                                   ; reg: 0x052
0f78:  0852  movf    0x52, W                                ; reg: 0x052
0f79:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0f7a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f7b:  3400  retlw   0x00

function_045:                                               ; address: 0x0f7c


; >>> RE NOTES @ 0x0F7C
; PARSE HEX BYTE routine. Reads two ASCII hex chars and combines them into one byte.
; <<<
0f7c:  272e  call    0x072e
0f7d:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0f7e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f7f:  00cf  movwf   0x4f                                   ; reg: 0x04f
0f80:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f81:  272e  call    0x072e
0f82:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0f83:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f84:  00d0  movwf   0x50                                   ; reg: 0x050
0f85:  084f  movf    0x4f, W                                ; reg: 0x04f
0f86:  00d1  movwf   0x51                                   ; reg: 0x051
0f87:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f88:  2760  call    0x0760
0f89:  0e78  swapf   (Common_RAM + 8), W                    ; reg: 0x078
0f8a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f8b:  00ce  movwf   0x4e                                   ; reg: 0x04e
0f8c:  30f0  movlw   0xf0
0f8d:  05ce  andwf   0x4e, F                                ; reg: 0x04e
0f8e:  0850  movf    0x50, W                                ; reg: 0x050
0f8f:  00d1  movwf   0x51                                   ; reg: 0x051
0f90:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f91:  2760  call    0x0760
0f92:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
0f93:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f94:  07ce  addwf   0x4e, F                                ; reg: 0x04e
0f95:  084e  movf    0x4e, W                                ; reg: 0x04e
0f96:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
0f97:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f98:  3400  retlw   0x00

function_046:                                               ; address: 0x0f99

0f99:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f9a:  0850  movf    0x50, W                                ; reg: 0x050
0f9b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f9c:  074a  addwf   0x4a, W                                ; reg: 0x04a
0f9d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0f9e:  00d1  movwf   0x51                                   ; reg: 0x051
0f9f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fa0:  084b  movf    0x4b, W                                ; reg: 0x04b
0fa1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fa2:  00d2  movwf   0x52                                   ; reg: 0x052
0fa3:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
0fa4:  0ad2  incf    0x52, F                                ; reg: 0x052
0fa5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fa6:  084b  movf    0x4b, W                                ; reg: 0x04b
0fa7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fa8:  0252  subwf   0x52, W                                ; reg: 0x052
0fa9:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0faa:  2fb9  goto    0x07b9
0fab:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
0fac:  2fb5  goto    0x07b5
0fad:  0851  movf    0x51, W                                ; reg: 0x051
0fae:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0faf:  024a  subwf   0x4a, W                                ; reg: 0x04a
0fb0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0fb1:  2fb4  goto    0x07b4
0fb2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fb3:  2fb9  goto    0x07b9
0fb4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fb5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fb6:  2000  call    0x0000
0fb7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fb8:  2fa5  goto    0x07a5
0fb9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fba:  3400  retlw   0x00

function_047:                                               ; address: 0x0fbb

0fbb:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6
0fbc:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
0fbd:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
0fbe:  2fbc  goto    0x07bc
0fbf:  301f  movlw   0x1f
0fc0:  0588  andwf   PORTD, F                               ; reg: 0x008
0fc1:  3080  movlw   0x80
0fc2:  0788  addwf   PORTD, F                               ; reg: 0x008
0fc3:  1051  bcf     0x51, 0x0                              ; reg: 0x051
0fc4:  1988  btfsc   PORTD, RD3                             ; reg: 0x008, bit: 3
0fc5:  1451  bsf     0x51, 0x0                              ; reg: 0x051
0fc6:  3020  movlw   0x20
0fc7:  0788  addwf   PORTD, F                               ; reg: 0x008
0fc8:  10d1  bcf     0x51, 0x1                              ; reg: 0x051
0fc9:  1988  btfsc   PORTD, RD3                             ; reg: 0x008, bit: 3
0fca:  14d1  bsf     0x51, 0x1                              ; reg: 0x051
0fcb:  3020  movlw   0x20
0fcc:  0788  addwf   PORTD, F                               ; reg: 0x008
0fcd:  1151  bcf     0x51, 0x2                              ; reg: 0x051
0fce:  1988  btfsc   PORTD, RD3                             ; reg: 0x008, bit: 3
0fcf:  1551  bsf     0x51, 0x2                              ; reg: 0x051
0fd0:  30c0  movlw   0xc0
0fd1:  048b  iorwf   INTCON, F                              ; reg: 0x00b
0fd2:  3400  retlw   0x00

function_048:                                               ; address: 0x0fd3

0fd3:  086f  movf    0x6f, W                                ; reg: 0x06f
0fd4:  3c05  sublw   0x05
0fd5:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
0fd6:  2fde  goto    0x07de
0fd7:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0fd8:  228d  call    0x028d
0fd9:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0fda:  12d6  bcf     0x56, 0x5                              ; reg: 0x056
0fdb:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0fdc:  21dc  call    0x01dc
0fdd:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0fde:  3400  retlw   0x00

function_049:                                               ; address: 0x0fdf

0fdf:  3001  movlw   0x01
0fe0:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fe1:  00d3  movwf   0x53                                   ; reg: 0x053
0fe2:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0fe3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fe4:  226d  call    0x026d
0fe5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0fe6:  3001  movlw   0x01
0fe7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
0fe8:  00d3  movwf   0x53                                   ; reg: 0x053
0fe9:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
0fea:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
0feb:  227d  call    0x027d
0fec:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
0fed:  1807  btfsc   PORTC, RC0                             ; reg: 0x007, bit: 0
0fee:  2ff3  goto    0x07f3
0fef:  1887  btfsc   PORTC, RC1                             ; reg: 0x007, bit: 1
0ff0:  2ff3  goto    0x07f3
0ff1:  13ad  bcf     0x2d, 0x7                              ; reg: 0x02d
0ff2:  2ff4  goto    0x07f4
0ff3:  17ad  bsf     0x2d, 0x7                              ; reg: 0x02d
0ff4:  3400  retlw   0x00

label_136:                                                  ; address: 0x0ff5

0ff5:  01cd  clrf    0x4d                                   ; reg: 0x04d
0ff6:  175d  bsf     0x5d, 0x6                              ; reg: 0x05d
0ff7:  11dd  bcf     0x5d, 0x3                              ; reg: 0x05d
0ff8:  12dd  bcf     0x5d, 0x5                              ; reg: 0x05d
0ff9:  13dd  bcf     0x5d, 0x7                              ; reg: 0x05d
0ffa:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a

label_137:                                                  ; address: 0x0ffb

0ffb:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
0ffc:  2b9a  goto    label_195

function_050:                                               ; address: 0x1000

1000:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1001:  26a9  call    function_027
1002:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1003:  3006  movlw   0x06
1004:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1005:  00d0  movwf   0x50                                   ; reg: 0x050
1006:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1007:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1008:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1009:  2799  call    function_046
100a:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
100b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
100c:  12dd  bcf     0x5d, 0x5                              ; reg: 0x05d
100d:  13dd  bcf     0x5d, 0x7                              ; reg: 0x05d
100e:  1f4f  btfss   0x4f, 0x6                              ; reg: 0x04f
100f:  2812  goto    label_138
1010:  3000  movlw   0x00
1011:  2813  goto    label_139

label_138:                                                  ; address: 0x1012

1012:  305a  movlw   0x5a

label_139:                                                  ; address: 0x1013

1013:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1014:  00ce  movwf   0x4e                                   ; reg: 0x04e
1015:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1016:  11d0  bcf     0x50, 0x3                              ; reg: 0x050

label_140:                                                  ; address: 0x1017

1017:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1018:  08ce  movf    0x4e, F                                ; reg: 0x04e
1019:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
101a:  287e  goto    label_152
101b:  01c0  clrf    0x40                                   ; reg: 0x040
101c:  01c1  clrf    0x41                                   ; reg: 0x041
101d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
101e:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
101f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1020:  24c3  call    function_043
1021:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1022:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1023:  303c  movlw   0x3c
1024:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1025:  00cf  movwf   0x4f                                   ; reg: 0x04f

label_141:                                                  ; address: 0x1026

1026:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1027:  1888  btfsc   PORTD, RD1                             ; reg: 0x008, bit: 1
1028:  282f  goto    label_143
1029:  19cf  btfsc   0x4f, 0x3                              ; reg: 0x04f
102a:  282d  goto    label_142
102b:  1c30  btfss   0x30, 0x0                              ; reg: 0x030
102c:  284b  goto    label_145

label_142:                                                  ; address: 0x102d

102d:  1b7e  btfsc   (Common_RAM + 14), 0x6                 ; reg: 0x07e
102e:  284b  goto    label_145

label_143:                                                  ; address: 0x102f

102f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1030:  08cf  movf    0x4f, F                                ; reg: 0x04f
1031:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1032:  2835  goto    label_144
1033:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1034:  284b  goto    label_145

label_144:                                                  ; address: 0x1035

1035:  01c0  clrf    0x40                                   ; reg: 0x040
1036:  01c1  clrf    0x41                                   ; reg: 0x041
1037:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1038:  1286  bcf     PORTB, RB5                             ; reg: 0x006, bit: 5
1039:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
103a:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
103b:  24c3  call    function_043
103c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
103d:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
103e:  3001  movlw   0x01
103f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1040:  00d0  movwf   0x50                                   ; reg: 0x050
1041:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1042:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1043:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1044:  2799  call    function_046
1045:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1046:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1047:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1048:  03cf  decf    0x4f, F                                ; reg: 0x04f
1049:  2826  goto    label_141
104a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_145:                                                  ; address: 0x104b

104b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
104c:  08cf  movf    0x4f, F                                ; reg: 0x04f
104d:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
104e:  2854  goto    label_146
104f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1050:  15b0  bsf     0x30, 0x3                              ; reg: 0x030
1051:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1052:  287e  goto    label_152
1053:  2858  goto    label_147

label_146:                                                  ; address: 0x1054

1054:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1055:  1686  bsf     PORTB, RB5                             ; reg: 0x006, bit: 5
1056:  134f  bcf     0x4f, 0x6                              ; reg: 0x04f
1057:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_147:                                                  ; address: 0x1058

1058:  3001  movlw   0x01
1059:  00d0  movwf   0x50                                   ; reg: 0x050
105a:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
105b:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
105c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
105d:  2799  call    function_046
105e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
105f:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1060:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1061:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1062:  27bb  call    function_047
1063:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1064:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1065:  3000  movlw   0x00
1066:  1c51  btfss   0x51, 0x0                              ; reg: 0x051
1067:  3001  movlw   0x01
1068:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1069:  00d0  movwf   0x50                                   ; reg: 0x050
106a:  3000  movlw   0x00
106b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
106c:  19d0  btfsc   0x50, 0x3                              ; reg: 0x050
106d:  3001  movlw   0x01
106e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
106f:  0650  xorwf   0x50, W                                ; reg: 0x050
1070:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1071:  2874  goto    label_148
1072:  03ce  decf    0x4e, F                                ; reg: 0x04e
1073:  287b  goto    label_150

label_148:                                                  ; address: 0x1074

1074:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1075:  19d0  btfsc   0x50, 0x3                              ; reg: 0x050
1076:  2879  goto    label_149
1077:  15d0  bsf     0x50, 0x3                              ; reg: 0x050
1078:  287c  goto    label_151

label_149:                                                  ; address: 0x1079

1079:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
107a:  287e  goto    label_152

label_150:                                                  ; address: 0x107b

107b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_151:                                                  ; address: 0x107c

107c:  2817  goto    label_140
107d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_152:                                                  ; address: 0x107e

107e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
107f:  1286  bcf     PORTB, RB5                             ; reg: 0x006, bit: 5
1080:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1081:  08ce  movf    0x4e, F                                ; reg: 0x04e
1082:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1083:  2888  goto    label_153
1084:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1085:  174f  bsf     0x4f, 0x6                              ; reg: 0x04f
1086:  15b0  bsf     0x30, 0x3                              ; reg: 0x030
1087:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_153:                                                  ; address: 0x1088

1088:  084e  movf    0x4e, W                                ; reg: 0x04e
1089:  3c5a  sublw   0x5a
108a:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
108b:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
108c:  0c77  rrf     (Common_RAM + 7), W                    ; reg: 0x077
108d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
108e:  00ab  movwf   0x2b                                   ; reg: 0x02b
108f:  3400  retlw   0x00
1090:  3007  movlw   0x07
1091:  00ad  movwf   0x2d                                   ; reg: 0x02d
1092:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1093:  226a  call    function_010
1094:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1095:  3012  movlw   0x12
1096:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1097:  00d0  movwf   0x50                                   ; reg: 0x050
1098:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1099:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
109a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
109b:  2799  call    function_046
109c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
109d:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
109e:  3001  movlw   0x01
109f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10a0:  00d3  movwf   0x53                                   ; reg: 0x053
10a1:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10a2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10a3:  226d  call    function_011
10a4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10a5:  3012  movlw   0x12
10a6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10a7:  00d0  movwf   0x50                                   ; reg: 0x050
10a8:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10a9:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
10aa:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10ab:  2799  call    function_046
10ac:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10ad:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
10ae:  0858  movf    0x58, W                                ; reg: 0x058
10af:  3c1d  sublw   0x1d
10b0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
10b1:  28b4  goto    label_154
10b2:  10ad  bcf     0x2d, 0x1                              ; reg: 0x02d
10b3:  112d  bcf     0x2d, 0x2                              ; reg: 0x02d

label_154:                                                  ; address: 0x10b4

10b4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10b5:  01d3  clrf    0x53                                   ; reg: 0x053
10b6:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10b7:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10b8:  226d  call    function_011
10b9:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10ba:  3001  movlw   0x01
10bb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10bc:  00d3  movwf   0x53                                   ; reg: 0x053
10bd:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10be:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10bf:  227d  call    0x027d
10c0:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10c1:  3012  movlw   0x12
10c2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10c3:  00d0  movwf   0x50                                   ; reg: 0x050
10c4:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10c5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
10c6:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10c7:  2799  call    function_046
10c8:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10c9:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
10ca:  0858  movf    0x58, W                                ; reg: 0x058
10cb:  3c1d  sublw   0x1d
10cc:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
10cd:  28d0  goto    label_155
10ce:  102d  bcf     0x2d, 0x0                              ; reg: 0x02d
10cf:  112d  bcf     0x2d, 0x2                              ; reg: 0x02d

label_155:                                                  ; address: 0x10d0

10d0:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10d1:  01d3  clrf    0x53                                   ; reg: 0x053
10d2:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10d3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10d4:  226d  call    function_011
10d5:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10d6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10d7:  01d3  clrf    0x53                                   ; reg: 0x053
10d8:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10d9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10da:  227d  call    0x027d
10db:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10dc:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10dd:  226a  call    0x026a
10de:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10df:  3400  retlw   0x00

label_156:                                                  ; address: 0x10e0

10e0:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10e1:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
10e2:  272e  call    function_044
10e3:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10e4:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
10e5:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
10e6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10e7:  00c8  movwf   0x48                                   ; reg: 0x048

; >>> RE NOTES @ 0x10E8
; COMMAND PARSER: first command byte must be ASCII 'C' (0x43).
; <<<
10e8:  3c43  sublw   0x43
10e9:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
10ea:  2aba  goto    label_181
10eb:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10ec:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
10ed:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10ee:  272e  call    function_044
10ef:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10f0:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
10f1:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
10f2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10f3:  00c9  movwf   0x49                                   ; reg: 0x049

; >>> RE NOTES @ 0x10F4
; COMMAND PARSER: second byte checked for ASCII 'W' (0x57). This begins CWxxYY write-command handling.
; <<<
10f4:  3c57  sublw   0x57
10f5:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
10f6:  2a0d  goto    label_164
10f7:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
10f8:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
10f9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
10fa:  277c  call    function_045
10fb:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
10fc:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
10fd:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
10fe:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
10ff:  00ca  movwf   0x4a                                   ; reg: 0x04a
1100:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1101:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1102:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1103:  277c  call    function_045
1104:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1105:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1106:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1107:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1108:  00cb  movwf   0x4b                                   ; reg: 0x04b
1109:  084a  movf    0x4a, W                                ; reg: 0x04a
110a:  3ef0  addlw   0xf0
110b:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
110c:  2a0c  goto    label_163
110d:  3e10  addlw   0x10
110e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
110f:  2b5a  goto    label_193
1110:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1111:  08cb  movf    0x4b, F                                ; reg: 0x04b
1112:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1113:  2915  goto    label_157
1114:  01c2  clrf    0x42                                   ; reg: 0x042

label_157:                                                  ; address: 0x1115

1115:  2a0c  goto    label_163
1116:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1117:  26f6  call    function_028
1118:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1119:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
111a:  018d  clrf    PIR2                                   ; reg: 0x00d
111b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
111c:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
111d:  0844  movf    0x44, W                                ; reg: 0x0c4
111e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
111f:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
1120:  008c  movwf   EEDATA                                 ; reg: 0x10c
1121:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1122:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
1123:  150c  bsf     EECON1, WREN                           ; reg: 0x18c, bit: 2
1124:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1125:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
1126:  080b  movf    INTCON, W                              ; reg: 0x00b
1127:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
1128:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
1129:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
112a:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
112b:  3055  movlw   0x55
112c:  008d  movwf   EECON2                                 ; reg: 0x18d
112d:  30aa  movlw   0xaa
112e:  008d  movwf   EECON2                                 ; reg: 0x18d
112f:  148c  bsf     EECON1, WR                             ; reg: 0x18c, bit: 1
1130:  188c  btfsc   EECON1, WR                             ; reg: 0x18c, bit: 1
1131:  2930  goto    0x0130
1132:  110c  bcf     EECON1, WREN                           ; reg: 0x18c, bit: 2
1133:  0877  movf    0x77, W                                ; reg: 0x1f7
1134:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1135:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
1136:  048b  iorwf   INTCON, F                              ; reg: 0x00b
1137:  3001  movlw   0x01
1138:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
1139:  008d  movwf   EEADR                                  ; reg: 0x10d
113a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
113b:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
113c:  0843  movf    0x43, W                                ; reg: 0x0c3
113d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
113e:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
113f:  008c  movwf   EEDATA                                 ; reg: 0x10c
1140:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1141:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
1142:  150c  bsf     EECON1, WREN                           ; reg: 0x18c, bit: 2
1143:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1144:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
1145:  080b  movf    INTCON, W                              ; reg: 0x00b
1146:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
1147:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
1148:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1149:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
114a:  3055  movlw   0x55
114b:  008d  movwf   EECON2                                 ; reg: 0x18d
114c:  30aa  movlw   0xaa
114d:  008d  movwf   EECON2                                 ; reg: 0x18d
114e:  148c  bsf     EECON1, WR                             ; reg: 0x18c, bit: 1
114f:  188c  btfsc   EECON1, WR                             ; reg: 0x18c, bit: 1
1150:  294f  goto    0x014f
1151:  110c  bcf     EECON1, WREN                           ; reg: 0x18c, bit: 2
1152:  0877  movf    0x77, W                                ; reg: 0x1f7
1153:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1154:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
1155:  048b  iorwf   INTCON, F                              ; reg: 0x00b
1156:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1157:  271e  call    0x071e
1158:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1159:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
115a:  2a0c  goto    0x020c
115b:  15d1  bsf     0x51, 0x3                              ; reg: 0x051
115c:  3078  movlw   0x78
115d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
115e:  00c2  movwf   0x42                                   ; reg: 0x042
115f:  2a0c  goto    0x020c
1160:  11d1  bcf     0x51, 0x3                              ; reg: 0x051
1161:  01cb  clrf    0x4b                                   ; reg: 0x04b
1162:  01ca  clrf    0x4a                                   ; reg: 0x04a
1163:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1164:  2a0c  goto    0x020c
1165:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1166:  084b  movf    0x4b, W                                ; reg: 0x04b
1167:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1168:  00c8  movwf   0x48                                   ; reg: 0x048
1169:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
116a:  219e  call    0x019e
116b:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
116c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
116d:  2a0c  goto    0x020c
116e:  2000  call    0x0000
116f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1170:  2a0c  goto    0x020c
1171:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1172:  226a  call    0x026a
1173:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1174:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1175:  2a0c  goto    0x020c
1176:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1177:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1178:  27d3  call    function_048
1179:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
117a:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
117b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
117c:  2a0c  goto    label_163
117d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
117e:  084b  movf    0x4b, W                                ; reg: 0x04b
117f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1180:  00a9  movwf   0x29                                   ; reg: 0x029
1181:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1182:  2a0c  goto    label_163
1183:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1184:  01cd  clrf    0x4d                                   ; reg: 0x04d
1185:  084b  movf    0x4b, W                                ; reg: 0x04b
1186:  00cc  movwf   0x4c                                   ; reg: 0x04c
1187:  084d  movf    0x4d, W                                ; reg: 0x04d
1188:  00d7  movwf   0x57                                   ; reg: 0x057
1189:  084c  movf    0x4c, W                                ; reg: 0x04c
118a:  00d6  movwf   0x56                                   ; reg: 0x056
118b:  01d9  clrf    0x59                                   ; reg: 0x059
118c:  3018  movlw   0x18
118d:  00d8  movwf   0x58                                   ; reg: 0x058
118e:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
118f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1190:  23b9  call    function_016
1191:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1192:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1193:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1194:  00cf  movwf   0x4f                                   ; reg: 0x04f
1195:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1196:  00ce  movwf   0x4e                                   ; reg: 0x04e
1197:  084f  movf    0x4f, W                                ; reg: 0x04f
1198:  00d3  movwf   0x53                                   ; reg: 0x053
1199:  084e  movf    0x4e, W                                ; reg: 0x04e
119a:  00d2  movwf   0x52                                   ; reg: 0x052
119b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
119c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
119d:  24ca  call    0x04ca
119e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
119f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11a0:  2a0c  goto    0x020c
11a1:  2090  call    0x0090
11a2:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11a3:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
11a4:  27d3  call    function_048
11a5:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11a6:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
11a7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11a8:  2a0c  goto    label_163
11a9:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11aa:  0e4b  swapf   0x4b, W                                ; reg: 0x04b
11ab:  00ce  movwf   0x4e                                   ; reg: 0x04e
11ac:  30f0  movlw   0xf0
11ad:  05ce  andwf   0x4e, F                                ; reg: 0x04e
11ae:  01d3  clrf    0x53                                   ; reg: 0x053
11af:  084e  movf    0x4e, W                                ; reg: 0x04e
11b0:  00d2  movwf   0x52                                   ; reg: 0x052
11b1:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11b2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
11b3:  2624  call    function_026
11b4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11b5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11b6:  2a0c  goto    0x020c
11b7:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11b8:  26a9  call    0x06a9
11b9:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11ba:  1ec3  btfss   0x43, 0x5                              ; reg: 0x043
11bb:  29be  goto    0x01be
11bc:  3021  movlw   0x21
11bd:  29bf  goto    0x01bf
11be:  3001  movlw   0x01
11bf:  00c3  movwf   0x43                                   ; reg: 0x043
11c0:  16c3  bsf     0x43, 0x5                              ; reg: 0x043
11c1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11c2:  2a0c  goto    0x020c
11c3:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11c4:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
11c5:  27df  call    function_049
11c6:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11c7:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
11c8:  3082  movlw   0x82
11c9:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11ca:  00c2  movwf   0x42                                   ; reg: 0x042
11cb:  3049  movlw   0x49

label_158:                                                  ; address: 0x11cc

11cc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
11cd:  1a0c  btfsc   PIR1, TXIF                             ; reg: 0x00c, bit: 4
11ce:  29d1  goto    label_159
11cf:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11d0:  29cc  goto    label_158

label_159:                                                  ; address: 0x11d1

11d1:  0099  movwf   TXREG                                  ; reg: 0x019
11d2:  300a  movlw   0x0a

label_160:                                                  ; address: 0x11d3

11d3:  1e0c  btfss   PIR1, TXIF                             ; reg: 0x00c, bit: 4
11d4:  29d3  goto    label_160
11d5:  0099  movwf   TXREG                                  ; reg: 0x019
11d6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11d7:  2a0c  goto    label_163
11d8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11d9:  084b  movf    0x4b, W                                ; reg: 0x04b
11da:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
11db:  00d2  movwf   0x52                                   ; reg: 0x052
11dc:  17dd  bsf     0x5d, 0x7                              ; reg: 0x05d
11dd:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11de:  2a0c  goto    label_163
11df:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11e0:  084b  movf    0x4b, W                                ; reg: 0x04b
11e1:  3cc4  sublw   0xc4
11e2:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
11e3:  2a0a  goto    label_162
11e4:  01cb  clrf    0x4b                                   ; reg: 0x04b
11e5:  084b  movf    0x4b, W                                ; reg: 0x04b
11e6:  3c13  sublw   0x13
11e7:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
11e8:  2a01  goto    label_161
11e9:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11ea:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
11eb:  276b  call    function_033
11ec:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11ed:  3032  movlw   0x32
11ee:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11ef:  00ce  movwf   0x4e                                   ; reg: 0x04e
11f0:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11f1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
11f2:  25cc  call    0x05cc
11f3:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11f4:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11f5:  276e  call    0x076e
11f6:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11f7:  3032  movlw   0x32
11f8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11f9:  00ce  movwf   0x4e                                   ; reg: 0x04e
11fa:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
11fb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
11fc:  25cc  call    0x05cc
11fd:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
11fe:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
11ff:  0acb  incf    0x4b, F                                ; reg: 0x04b
1200:  29e5  goto    0x01e5

label_161:                                                  ; address: 0x1201

1201:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1202:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6
1203:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
1204:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
1205:  2a03  goto    0x0203
1206:  2a06  goto    0x0206
1207:  018a  clrf    PCLATH                                 ; reg: 0x00a
1208:  2800  goto    vector_reset
1209:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_162:                                                  ; address: 0x120a

120a:  2a0c  goto    label_057
120b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_163:                                                  ; address: 0x120c

120c:  2b51  goto    label_064

label_164:                                                  ; address: 0x120d


; >>> RE NOTES @ 0x120D
; READ COMMAND branch: second byte must be ASCII 'R' (0x52). This begins CRxx handling.
; <<<
120d:  0849  movf    0x49, W                                ; reg: 0x049
120e:  3c52  sublw   0x52
120f:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1210:  2aba  goto    label_063
1211:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1212:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1213:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

; >>> RE NOTES @ 0x1214
; CRxx: parse two ASCII hex digits into register/index byte.
; <<<
1214:  277c  call    function_045
1215:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1216:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1217:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1218:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1219:  00ca  movwf   0x4a                                   ; reg: 0x04a
121a:  01cb  clrf    0x4b                                   ; reg: 0x04b
121b:  084a  movf    0x4a, W                                ; reg: 0x04a
121c:  3ef1  addlw   0xf1
121d:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
121e:  2ab9  goto    label_180
121f:  3e0f  addlw   0x0f
1220:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

; >>> RE NOTES @ 0x1221
; CR read dispatch jump table target. Valid low register range maps through table at 0x136E.
; <<<
1221:  2b6e  goto    label_194
1222:  01d3  clrf    0x53                                   ; reg: 0x053
1223:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1224:  2ab9  goto    label_180
1225:  0853  movf    0x53, W                                ; reg: 0x053
1226:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1227:  00cb  movwf   0x4b                                   ; reg: 0x04b
1228:  2ab9  goto    label_180

; >>> RE NOTES @ 0x1229
; CR02 handler: samples multiplexed RD3 states plus direct digital inputs RD0, RD1, RD4, RE1 into one returned status byte.
; <<<
1229:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
122a:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
122b:  27bb  call    function_047
122c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
122d:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
122e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
122f:  01cb  clrf    0x4b                                   ; reg: 0x04b
1230:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1231:  1c51  btfss   0x51, 0x0                              ; reg: 0x051
1232:  2a36  goto    label_165
1233:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1234:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
1235:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_165:                                                  ; address: 0x1236

1236:  1cd1  btfss   0x51, 0x1                              ; reg: 0x051
1237:  2a3b  goto    label_166
1238:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1239:  14cb  bsf     0x4b, 0x1                              ; reg: 0x04b
123a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_166:                                                  ; address: 0x123b

123b:  1d51  btfss   0x51, 0x2                              ; reg: 0x051
123c:  2a40  goto    label_167
123d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
123e:  154b  bsf     0x4b, 0x2                              ; reg: 0x04b
123f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_167:                                                  ; address: 0x1240

1240:  1dd1  btfss   0x51, 0x3                              ; reg: 0x051
1241:  2a45  goto    label_168
1242:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1243:  15cb  bsf     0x4b, 0x3                              ; reg: 0x04b
1244:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_168:                                                  ; address: 0x1245

1245:  1c08  btfss   PORTD, RD0                             ; reg: 0x008, bit: 0
1246:  2a4a  goto    label_169
1247:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1248:  164b  bsf     0x4b, 0x4                              ; reg: 0x04b
1249:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_169:                                                  ; address: 0x124a

124a:  1c88  btfss   PORTD, RD1                             ; reg: 0x008, bit: 1
124b:  2a4f  goto    label_170
124c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
124d:  16cb  bsf     0x4b, 0x5                              ; reg: 0x04b
124e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_170:                                                  ; address: 0x124f

124f:  1e08  btfss   PORTD, RD4                             ; reg: 0x008, bit: 4
1250:  2a54  goto    label_171
1251:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1252:  174b  bsf     0x4b, 0x6                              ; reg: 0x04b
1253:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_171:                                                  ; address: 0x1254

1254:  1c89  btfss   PORTE, RE1                             ; reg: 0x009, bit: 1
1255:  2a59  goto    label_172
1256:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1257:  17cb  bsf     0x4b, 0x7                              ; reg: 0x04b
1258:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_172:                                                  ; address: 0x1259

1259:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
125a:  2ab9  goto    label_180

; >>> RE NOTES @ 0x125B
; CR03 handler: returns status/output bits including RB1, RB5 and internal state bits.
; <<<
125b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
125c:  01cb  clrf    0x4b                                   ; reg: 0x04b
125d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
125e:  1c86  btfss   PORTB, RB1                             ; reg: 0x006, bit: 1
125f:  2a63  goto    label_173
1260:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1261:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
1262:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_173:                                                  ; address: 0x1263

1263:  1e86  btfss   PORTB, RB5                             ; reg: 0x006, bit: 5
1264:  2a68  goto    label_174
1265:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1266:  14cb  bsf     0x4b, 0x1                              ; reg: 0x04b
1267:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_174:                                                  ; address: 0x1268

1268:  1ed6  btfss   0x56, 0x5                              ; reg: 0x056
1269:  2a6d  goto    label_175
126a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
126b:  154b  bsf     0x4b, 0x2                              ; reg: 0x04b
126c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_175:                                                  ; address: 0x126d

126d:  1fd6  btfss   0x56, 0x7                              ; reg: 0x056
126e:  2a72  goto    label_176
126f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1270:  15cb  bsf     0x4b, 0x3                              ; reg: 0x04b
1271:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_176:                                                  ; address: 0x1272

1272:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1273:  2ab9  goto    label_180
1274:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1275:  0822  movf    0x22, W                                ; reg: 0x022
1276:  00cb  movwf   0x4b                                   ; reg: 0x04b
1277:  2ab9  goto    label_180
1278:  0834  movf    0x34, W                                ; reg: 0x034
1279:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
127a:  00cb  movwf   0x4b                                   ; reg: 0x04b
127b:  2ab9  goto    label_180

; >>> RE NOTES @ 0x127C
; CR06 handler: returns internal flags plus RB4 state.
; <<<
127c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
127d:  01cb  clrf    0x4b                                   ; reg: 0x04b
127e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
127f:  1c2d  btfss   0x2d, 0x0                              ; reg: 0x02d
1280:  2a84  goto    label_177
1281:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1282:  144b  bsf     0x4b, 0x0                              ; reg: 0x04b
1283:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_177:                                                  ; address: 0x1284

1284:  1cad  btfss   0x2d, 0x1                              ; reg: 0x02d
1285:  2a89  goto    label_178
1286:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1287:  14cb  bsf     0x4b, 0x1                              ; reg: 0x04b
1288:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_178:                                                  ; address: 0x1289

1289:  1e06  btfss   PORTB, RB4                             ; reg: 0x006, bit: 4
128a:  2a8e  goto    label_179
128b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
128c:  154b  bsf     0x4b, 0x2                              ; reg: 0x04b
128d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_179:                                                  ; address: 0x128e

128e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
128f:  2ab9  goto    label_180
1290:  0c45  rrf     0x45, W                                ; reg: 0x045
1291:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1292:  0c44  rrf     0x44, W                                ; reg: 0x044
1293:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
1294:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
1295:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
1296:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
1297:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
1298:  0cfa  rrf     (Common_RAM + 10), F                   ; reg: 0x07a
1299:  0cf9  rrf     (Common_RAM + 9), F                    ; reg: 0x079
129a:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
129b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
129c:  00cb  movwf   0x4b                                   ; reg: 0x04b
129d:  2ab9  goto    label_180
129e:  3007  movlw   0x07
129f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12a0:  00cb  movwf   0x4b                                   ; reg: 0x04b
12a1:  2ab9  goto    label_180
12a2:  082e  movf    0x2e, W                                ; reg: 0x02e
12a3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12a4:  00cb  movwf   0x4b                                   ; reg: 0x04b
12a5:  2ab9  goto    label_180
12a6:  082f  movf    0x2f, W                                ; reg: 0x02f
12a7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12a8:  00cb  movwf   0x4b                                   ; reg: 0x04b
12a9:  2ab9  goto    label_180
12aa:  3002  movlw   0x02
12ab:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12ac:  00cb  movwf   0x4b                                   ; reg: 0x04b
12ad:  2ab9  goto    label_180
12ae:  3071  movlw   0x71
12af:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12b0:  00cb  movwf   0x4b                                   ; reg: 0x04b
12b1:  2ab9  goto    label_180
12b2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12b3:  01cb  clrf    0x4b                                   ; reg: 0x04b
12b4:  2ab9  goto    label_180
12b5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12b6:  01cb  clrf    0x4b                                   ; reg: 0x04b
12b7:  2ab9  goto    label_180
12b8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_180:                                                  ; address: 0x12b9


; >>> RE NOTES @ 0x12B9
; Common CR response path.
; <<<
12b9:  2b2f  goto    label_187

label_181:                                                  ; address: 0x12ba

12ba:  0848  movf    0x48, W                                ; reg: 0x048
12bb:  3c41  sublw   0x41
12bc:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
12bd:  2b2e  goto    label_186
12be:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
12bf:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
12c0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
12c1:  272e  call    function_044
12c2:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
12c3:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
12c4:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
12c5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12c6:  00c9  movwf   0x49                                   ; reg: 0x049
12c7:  0849  movf    0x49, W                                ; reg: 0x049
12c8:  3c57  sublw   0x57
12c9:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
12ca:  2b10  goto    label_184
12cb:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
12cc:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
12cd:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
12ce:  277c  call    function_045
12cf:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
12d0:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
12d1:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
12d2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12d3:  00ca  movwf   0x4a                                   ; reg: 0x04a
12d4:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
12d5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
12d6:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
12d7:  277c  call    function_045
12d8:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
12d9:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
12da:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
12db:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12dc:  00cb  movwf   0x4b                                   ; reg: 0x04b
12dd:  0848  movf    0x48, W                                ; reg: 0x048
12de:  3c41  sublw   0x41
12df:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
12e0:  2b0f  goto    label_183
12e1:  084a  movf    0x4a, W                                ; reg: 0x04a
12e2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
12e3:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
12e4:  008d  movwf   EEADR                                  ; reg: 0x10d
12e5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12e6:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
12e7:  084b  movf    0x4b, W                                ; reg: 0x0cb
12e8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
12e9:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
12ea:  008c  movwf   EEDATA                                 ; reg: 0x10c
12eb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12ec:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
12ed:  150c  bsf     EECON1, WREN                           ; reg: 0x18c, bit: 2
12ee:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
12ef:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
12f0:  080b  movf    INTCON, W                              ; reg: 0x00b
12f1:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
12f2:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
12f3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
12f4:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
12f5:  3055  movlw   0x55
12f6:  008d  movwf   EECON2                                 ; reg: 0x18d
12f7:  30aa  movlw   0xaa
12f8:  008d  movwf   EECON2                                 ; reg: 0x18d
12f9:  148c  bsf     EECON1, WR                             ; reg: 0x18c, bit: 1

label_182:                                                  ; address: 0x12fa

12fa:  188c  btfsc   PIR1, TMR2IF                           ; reg: 0x00c, bit: 1
12fb:  2afa  goto    label_182
12fc:  110c  bcf     PIR1, CCP1IF                           ; reg: 0x00c, bit: 2
12fd:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
12fe:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
12ff:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
1300:  048b  iorwf   INTCON, F                              ; reg: 0x00b
1301:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1302:  084a  movf    0x4a, W                                ; reg: 0x0ca
1303:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1304:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
1305:  008d  movwf   EEADR                                  ; reg: 0x10d
1306:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1307:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
1308:  140c  bsf     EECON1, RD                             ; reg: 0x18c, bit: 0
1309:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
130a:  080c  movf    EEDATA, W                              ; reg: 0x10c
130b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
130c:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
130d:  00cb  movwf   0x4b                                   ; reg: 0x0cb
130e:  2b0f  goto    label_183

label_183:                                                  ; address: 0x130f

130f:  2b2f  goto    label_187

label_184:                                                  ; address: 0x1310

1310:  0849  movf    0x49, W                                ; reg: 0x049
1311:  3c52  sublw   0x52
1312:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1313:  2b2e  goto    label_186
1314:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1315:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1316:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1317:  277c  call    function_045
1318:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1319:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
131a:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
131b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
131c:  00ca  movwf   0x4a                                   ; reg: 0x04a
131d:  0848  movf    0x48, W                                ; reg: 0x048
131e:  3c41  sublw   0x41
131f:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1320:  2b2d  goto    label_185
1321:  084a  movf    0x4a, W                                ; reg: 0x04a
1322:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1323:  1703  bsf     STATUS, RP1                            ; reg: 0x003, bit: 6
1324:  008d  movwf   EEADR                                  ; reg: 0x10d
1325:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1326:  138c  bcf     EECON1, EEPGD                          ; reg: 0x18c, bit: 7
1327:  140c  bsf     EECON1, RD                             ; reg: 0x18c, bit: 0
1328:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1329:  080c  movf    EEDATA, W                              ; reg: 0x10c
132a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
132b:  1303  bcf     STATUS, RP1                            ; reg: 0x003, bit: 6
132c:  00cb  movwf   0x4b                                   ; reg: 0x0cb

label_185:                                                  ; address: 0x132d

132d:  2b2f  goto    label_187

label_186:                                                  ; address: 0x132e

132e:  2b54  goto    label_192

label_187:                                                  ; address: 0x132f


; >>> RE NOTES @ 0x132F
; SERIAL RESPONSE formatter: emits command prefix bytes, register/index as hex, value as hex, then LF.
; <<<
132f:  0848  movf    0x48, W                                ; reg: 0x048

label_188:                                                  ; address: 0x1330

1330:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1331:  1a0c  btfsc   PIR1, TXIF                             ; reg: 0x00c, bit: 4
1332:  2b35  goto    label_189
1333:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1334:  2b30  goto    label_188

label_189:                                                  ; address: 0x1335

1335:  0099  movwf   TXREG                                  ; reg: 0x019
1336:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1337:  0849  movf    0x49, W                                ; reg: 0x049

label_190:                                                  ; address: 0x1338

1338:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1339:  1a0c  btfsc   PIR1, TXIF                             ; reg: 0x00c, bit: 4
133a:  2b3d  goto    label_191
133b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
133c:  2b38  goto    label_190

label_191:                                                  ; address: 0x133d

133d:  0099  movwf   TXREG                                  ; reg: 0x019
133e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
133f:  084a  movf    0x4a, W                                ; reg: 0x04a
1340:  00d6  movwf   0x56                                   ; reg: 0x056
1341:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1342:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1343:  22ad  call    function_013
1344:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1345:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1346:  084b  movf    0x4b, W                                ; reg: 0x04b
1347:  00d6  movwf   0x56                                   ; reg: 0x056
1348:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1349:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
134a:  22ad  call    0x02ad
134b:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
134c:  300a  movlw   0x0a
134d:  1e0c  btfss   PIR1, TXIF                             ; reg: 0x00c, bit: 4
134e:  2b4d  goto    0x034d
134f:  0099  movwf   TXREG                                  ; reg: 0x019
1350:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1351:  3001  movlw   0x01
1352:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1353:  2b56  goto    0x0356

label_192:                                                  ; address: 0x1354

1354:  3000  movlw   0x00
1355:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1356:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1357:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1358:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1359:  28c8  goto    label_243

label_193:                                                  ; address: 0x135a

135a:  140a  bsf     PCLATH, 0x0                            ; reg: 0x00a
135b:  148a  bsf     PCLATH, 0x1                            ; reg: 0x00a
135c:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
135d:  0782  addwf   PCL, F                                 ; reg: 0x002
135e:  2910  goto    label_250
135f:  2916  goto    label_251
1360:  295b  goto    label_260
1361:  2960  goto    label_261
1362:  2965  goto    label_263
1363:  296e  goto    label_265
1364:  2971  goto    label_266
1365:  2976  goto    label_267
1366:  297d  goto    label_268
1367:  2983  goto    label_271
1368:  29a1  goto    label_277
1369:  29a9  goto    label_278
136a:  29b7  goto    label_279
136b:  29c3  goto    label_281
136c:  29d8  goto    label_284
136d:  29df  goto    label_286

label_194:                                                  ; address: 0x136e


; >>> RE NOTES @ 0x136E
; CRxx DISPATCH TABLE. Entries 0x00..0x0E map to handlers at 0x1222..0x12B5.
; <<<
136e:  140a  bsf     PCLATH, 0x0                            ; reg: 0x00a
136f:  148a  bsf     PCLATH, 0x1                            ; reg: 0x00a
1370:  110a  bcf     PCLATH, 0x2                            ; reg: 0x00a
1371:  0782  addwf   PCL, F                                 ; reg: 0x002
1372:  2a22  goto    label_287
1373:  2a25  goto    label_288
1374:  2a29  goto    label_289
1375:  2a5b  goto    label_291
1376:  2a74  goto    label_295
1377:  2a78  goto    label_296
1378:  2a7c  goto    label_297
1379:  2a90  goto    label_298
137a:  2a9e  goto    label_299
137b:  2aa2  goto    label_300
137c:  2aa6  goto    label_301
137d:  2aaa  goto    label_303
137e:  2aae  goto    label_304
137f:  2ab2  goto    label_305
1380:  2ab5  goto    label_306

function_051:                                               ; address: 0x1381

1381:  01cf  clrf    0x4f                                   ; reg: 0x04f
1382:  01bb  clrf    0x3b                                   ; reg: 0x03b
1383:  1130  bcf     0x30, 0x2                              ; reg: 0x030
1384:  01bc  clrf    0x3c                                   ; reg: 0x03c
1385:  1ec3  btfss   0x43, 0x5                              ; reg: 0x043
1386:  2b89  goto    label_317
1387:  3021  movlw   0x21
1388:  2b8a  goto    label_318
1389:  3001  movlw   0x01
138a:  00c3  movwf   0x43                                   ; reg: 0x043
138b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
138c:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
138d:  24c3  call    function_043
138e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
138f:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1390:  3400  retlw   0x00
1391:  1f7e  btfss   (Common_RAM + 14), 0x6                 ; reg: 0x07e
1392:  2bb1  goto    label_196
1393:  3010  movlw   0x10
1394:  00cc  movwf   0x4c                                   ; reg: 0x04c
1395:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
1396:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
1397:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1398:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1399:  2ff5  goto    label_136

label_195:                                                  ; address: 0x139a

139a:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
139b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
139c:  1b30  btfsc   0x30, 0x6                              ; reg: 0x030
139d:  2bb1  goto    label_196
139e:  16c3  bsf     0x43, 0x5                              ; reg: 0x043
139f:  2000  call    function_050
13a0:  1686  bsf     PORTB, RB5                             ; reg: 0x006, bit: 5
13a1:  082b  movf    0x2b, W                                ; reg: 0x02b
13a2:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13a3:  00d0  movwf   0x50                                   ; reg: 0x050
13a4:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
13a5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
13a6:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13a7:  2799  call    function_046
13a8:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
13a9:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
13aa:  1286  bcf     PORTB, RB5                             ; reg: 0x006, bit: 5
13ab:  1730  bsf     0x30, 0x6                              ; reg: 0x030
13ac:  13fe  bcf     (Common_RAM + 14), 0x7                 ; reg: 0x07e
13ad:  137e  bcf     (Common_RAM + 14), 0x6                 ; reg: 0x07e
13ae:  3001  movlw   0x01
13af:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
13b0:  2bb3  goto    label_197

label_196:                                                  ; address: 0x13b1

13b1:  3000  movlw   0x00
13b2:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078

label_197:                                                  ; address: 0x13b3

13b3:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
13b4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
13b5:  28f4  goto    label_249

label_198:                                                  ; address: 0x13b6

13b6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13b7:  0848  movf    0x48, W                                ; reg: 0x048
13b8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13b9:  074a  addwf   0x4a, W                                ; reg: 0x04a
13ba:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13bb:  00c9  movwf   0x49                                   ; reg: 0x049
13bc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13bd:  084b  movf    0x4b, W                                ; reg: 0x04b
13be:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13bf:  00ca  movwf   0x4a                                   ; reg: 0x04a
13c0:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
13c1:  0aca  incf    0x4a, F                                ; reg: 0x04a

label_199:                                                  ; address: 0x13c2

13c2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13c3:  084b  movf    0x4b, W                                ; reg: 0x04b
13c4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13c5:  024a  subwf   0x4a, W                                ; reg: 0x04a
13c6:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
13c7:  2bda  goto    label_326
13c8:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
13c9:  2bd2  goto    label_325
13ca:  0849  movf    0x49, W                                ; reg: 0x049
13cb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13cc:  024a  subwf   0x4a, W                                ; reg: 0x04a
13cd:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
13ce:  2bd1  goto    label_324
13cf:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13d0:  2bda  goto    label_326
13d1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13d2:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
13d3:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
13d4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13d5:  2000  call    function_036
13d6:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
13d7:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
13d8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13d9:  2bc2  goto    label_199
13da:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13db:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
13dc:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
13dd:  2bf2  goto    label_202

label_200:                                                  ; address: 0x13de

13de:  01cb  clrf    0x4b                                   ; reg: 0x04b
13df:  01ca  clrf    0x4a                                   ; reg: 0x04a
13e0:  1bcf  btfsc   0x4f, 0x7                              ; reg: 0x04f
13e1:  2bfd  goto    label_206
13e2:  1bc3  btfsc   0x43, 0x7                              ; reg: 0x043
13e3:  2bfd  goto    label_206
13e4:  13c3  bcf     0x43, 0x7                              ; reg: 0x043
13e5:  1643  bsf     0x43, 0x4                              ; reg: 0x043

label_201:                                                  ; address: 0x13e6

13e6:  08cb  movf    0x4b, F                                ; reg: 0x04b
13e7:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
13e8:  2bfc  goto    label_205
13e9:  084a  movf    0x4a, W                                ; reg: 0x04a
13ea:  3c77  sublw   0x77
13eb:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
13ec:  2bfc  goto    label_205
13ed:  3001  movlw   0x01
13ee:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
13ef:  00c8  movwf   0x48                                   ; reg: 0x048
13f0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
13f1:  2bb6  goto    label_198

label_202:                                                  ; address: 0x13f2

13f2:  1fc3  btfss   0x43, 0x7                              ; reg: 0x043
13f3:  2bf5  goto    label_203
13f4:  2bfc  goto    label_205

label_203:                                                  ; address: 0x13f5

13f5:  1486  bsf     PORTB, RB1                             ; reg: 0x006, bit: 1
13f6:  1fdd  btfss   0x5d, 0x7                              ; reg: 0x05d
13f7:  2bfb  goto    label_204
13f8:  1edd  btfss   0x5d, 0x5                              ; reg: 0x05d
13f9:  2bfb  goto    label_204
13fa:  2bfc  goto    label_205

label_204:                                                  ; address: 0x13fb

13fb:  2be6  goto    label_201

label_205:                                                  ; address: 0x13fc

13fc:  1086  bcf     PORTB, RB1                             ; reg: 0x006, bit: 1

label_206:                                                  ; address: 0x13fd

13fd:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
13fe:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
13ff:  2946  goto    label_256

function_052:                                               ; address: 0x1400

1400:  2000  call    function_061
1401:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1402:  2255  call    0x0255
1403:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1404:  01cb  clrf    0x4b                                   ; reg: 0x04b
1405:  01ca  clrf    0x4a                                   ; reg: 0x04a
1406:  3037  movlw   0x37
1407:  00ad  movwf   0x2d                                   ; reg: 0x02d
1408:  1cd0  btfss   0x50, 0x1                              ; reg: 0x050
1409:  2c0e  goto    0x040e
140a:  3047  movlw   0x47
140b:  00ad  movwf   0x2d                                   ; reg: 0x02d
140c:  10d0  bcf     0x50, 0x1                              ; reg: 0x050
140d:  2c2f  goto    0x042f
140e:  3057  movlw   0x57
140f:  00ad  movwf   0x2d                                   ; reg: 0x02d
1410:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1411:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1412:  2113  call    function_040
1413:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1414:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1415:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1416:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1417:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1418:  023a  subwf   0x3a, W                                ; reg: 0x03a
1419:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
141a:  2c2d  goto    label_208
141b:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
141c:  2c21  goto    label_207
141d:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
141e:  0239  subwf   0x39, W                                ; reg: 0x039
141f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1420:  2c2d  goto    label_208

label_207:                                                  ; address: 0x1421

1421:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1422:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1423:  2113  call    function_040
1424:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1425:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1426:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1427:  02b9  subwf   0x39, F                                ; reg: 0x039
1428:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1429:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
142a:  0f79  incfsz  (Common_RAM + 9), W                    ; reg: 0x079
142b:  02ba  subwf   0x3a, F                                ; reg: 0x03a
142c:  2c2f  goto    label_209

label_208:                                                  ; address: 0x142d

142d:  01ba  clrf    0x3a                                   ; reg: 0x03a
142e:  01b9  clrf    0x39                                   ; reg: 0x039

label_209:                                                  ; address: 0x142f

142f:  3067  movlw   0x67
1430:  00ad  movwf   0x2d                                   ; reg: 0x02d
1431:  3400  retlw   0x00

function_053:                                               ; address: 0x1432

1432:  084d  movf    0x4d, W                                ; reg: 0x04d
1433:  3c01  sublw   0x01
1434:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1435:  2c3a  goto    label_210
1436:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
1437:  3001  movlw   0x01
1438:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1439:  2c59  goto    label_214

label_210:                                                  ; address: 0x143a

143a:  1d30  btfss   0x30, 0x2                              ; reg: 0x030
143b:  2c41  goto    label_211
143c:  3007  movlw   0x07
143d:  00ad  movwf   0x2d                                   ; reg: 0x02d
143e:  3001  movlw   0x01
143f:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1440:  2c59  goto    label_214

label_211:                                                  ; address: 0x1441

1441:  084f  movf    0x4f, W                                ; reg: 0x04f
1442:  39f7  andlw   0xf7
1443:  3c40  sublw   0x40
1444:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1445:  2c4e  goto    label_212
1446:  084f  movf    0x4f, W                                ; reg: 0x04f
1447:  39f7  andlw   0xf7
1448:  3c43  sublw   0x43
1449:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
144a:  2c4e  goto    label_212
144b:  3000  movlw   0x00
144c:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
144d:  2c59  goto    label_214

label_212:                                                  ; address: 0x144e

144e:  084f  movf    0x4f, W                                ; reg: 0x04f
144f:  39f7  andlw   0xf7
1450:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1451:  2c57  goto    label_213
1452:  3007  movlw   0x07
1453:  00ad  movwf   0x2d                                   ; reg: 0x02d
1454:  3001  movlw   0x01
1455:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1456:  2c59  goto    label_214

label_213:                                                  ; address: 0x1457

1457:  3000  movlw   0x00
1458:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078

label_214:                                                  ; address: 0x1459

1459:  3400  retlw   0x00

label_215:                                                  ; address: 0x145a

145a:  01f7  clrf    (Common_RAM + 7)                       ; reg: 0x077
145b:  01f8  clrf    (Common_RAM + 8)                       ; reg: 0x078
145c:  01f9  clrf    (Common_RAM + 9)                       ; reg: 0x079
145d:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
145e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
145f:  01e0  clrf    0x60                                   ; reg: 0x060
1460:  01e1  clrf    0x61                                   ; reg: 0x061
1461:  01e2  clrf    0x62                                   ; reg: 0x062
1462:  01e3  clrf    0x63                                   ; reg: 0x063
1463:  085f  movf    0x5f, W                                ; reg: 0x05f
1464:  045e  iorwf   0x5e, W                                ; reg: 0x05e
1465:  045d  iorwf   0x5d, W                                ; reg: 0x05d
1466:  045c  iorwf   0x5c, W                                ; reg: 0x05c
1467:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1468:  2c99  goto    label_219
1469:  3020  movlw   0x20
146a:  00e4  movwf   0x64                                   ; reg: 0x064

label_216:                                                  ; address: 0x146b

146b:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
146c:  0dd8  rlf     0x58, F                                ; reg: 0x058
146d:  0dd9  rlf     0x59, F                                ; reg: 0x059
146e:  0dda  rlf     0x5a, F                                ; reg: 0x05a
146f:  0ddb  rlf     0x5b, F                                ; reg: 0x05b
1470:  0de0  rlf     0x60, F                                ; reg: 0x060
1471:  0de1  rlf     0x61, F                                ; reg: 0x061
1472:  0de2  rlf     0x62, F                                ; reg: 0x062
1473:  0de3  rlf     0x63, F                                ; reg: 0x063
1474:  085f  movf    0x5f, W                                ; reg: 0x05f
1475:  0263  subwf   0x63, W                                ; reg: 0x063
1476:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1477:  2c82  goto    label_217
1478:  085e  movf    0x5e, W                                ; reg: 0x05e
1479:  0262  subwf   0x62, W                                ; reg: 0x062
147a:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
147b:  2c82  goto    label_217
147c:  085d  movf    0x5d, W                                ; reg: 0x05d
147d:  0261  subwf   0x61, W                                ; reg: 0x061
147e:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
147f:  2c82  goto    label_217
1480:  085c  movf    0x5c, W                                ; reg: 0x05c
1481:  0260  subwf   0x60, W                                ; reg: 0x060

label_217:                                                  ; address: 0x1482

1482:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1483:  2c93  goto    label_218
1484:  085c  movf    0x5c, W                                ; reg: 0x05c
1485:  02e0  subwf   0x60, F                                ; reg: 0x060
1486:  085d  movf    0x5d, W                                ; reg: 0x05d
1487:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1488:  0f5d  incfsz  0x5d, W                                ; reg: 0x05d
1489:  02e1  subwf   0x61, F                                ; reg: 0x061
148a:  085e  movf    0x5e, W                                ; reg: 0x05e
148b:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
148c:  0f5e  incfsz  0x5e, W                                ; reg: 0x05e
148d:  02e2  subwf   0x62, F                                ; reg: 0x062
148e:  085f  movf    0x5f, W                                ; reg: 0x05f
148f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1490:  0f5f  incfsz  0x5f, W                                ; reg: 0x05f
1491:  02e3  subwf   0x63, F                                ; reg: 0x063
1492:  1403  bsf     STATUS, C                              ; reg: 0x003, bit: 0

label_218:                                                  ; address: 0x1493

1493:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
1494:  0df8  rlf     (Common_RAM + 8), F                    ; reg: 0x078
1495:  0df9  rlf     (Common_RAM + 9), F                    ; reg: 0x079
1496:  0dfa  rlf     (Common_RAM + 10), F                   ; reg: 0x07a
1497:  0be4  decfsz  0x64, F                                ; reg: 0x064
1498:  2c6b  goto    label_216

label_219:                                                  ; address: 0x1499

1499:  0000  nop
149a:  30e0  movlw   0xe0
149b:  0084  movwf   FSR                                    ; reg: 0x004
149c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
149d:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
149e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
149f:  2d19  goto    label_221

function_054:                                               ; address: 0x14a0

14a0:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
14a1:  0851  movf    0x51, W                                ; reg: 0x051
14a2:  00c7  movwf   0x47                                   ; reg: 0x047
14a3:  0850  movf    0x50, W                                ; reg: 0x050
14a4:  00c6  movwf   0x46                                   ; reg: 0x046
14a5:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
14a6:  1250  bcf     0x50, 0x4                              ; reg: 0x050
14a7:  086e  movf    0x6e, W                                ; reg: 0x06e
14a8:  3c02  sublw   0x02
14a9:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
14aa:  2ccc  goto    label_220
14ab:  084c  movf    0x4c, W                                ; reg: 0x04c
14ac:  3970  andlw   0x70
14ad:  3c40  sublw   0x40
14ae:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
14af:  2ccc  goto    label_220
14b0:  306d  movlw   0x6d
14b1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
14b2:  00da  movwf   0x5a                                   ; reg: 0x05a
14b3:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
14b4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
14b5:  23d0  call    function_017
14b6:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
14b7:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
14b8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
14b9:  00d8  movwf   0x58                                   ; reg: 0x058
14ba:  0851  movf    0x51, W                                ; reg: 0x051
14bb:  00db  movwf   0x5b                                   ; reg: 0x05b
14bc:  0850  movf    0x50, W                                ; reg: 0x050
14bd:  00da  movwf   0x5a                                   ; reg: 0x05a
14be:  01dd  clrf    0x5d                                   ; reg: 0x05d
14bf:  0858  movf    0x58, W                                ; reg: 0x058
14c0:  00dc  movwf   0x5c                                   ; reg: 0x05c
14c1:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
14c2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
14c3:  23e7  call    0x03e7
14c4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
14c5:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
14c6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
14c7:  00d1  movwf   0x51                                   ; reg: 0x051
14c8:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
14c9:  00d0  movwf   0x50                                   ; reg: 0x050
14ca:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
14cb:  1650  bsf     0x50, 0x4                              ; reg: 0x050

label_220:                                                  ; address: 0x14cc

14cc:  1c7e  btfss   (Common_RAM + 14), 0x0                 ; reg: 0x07e
14cd:  2d3f  goto    0x053f
14ce:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
14cf:  0852  movf    0x52, W                                ; reg: 0x052
14d0:  00da  movwf   0x5a                                   ; reg: 0x05a
14d1:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
14d2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
14d3:  23d0  call    0x03d0
14d4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
14d5:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
14d6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
14d7:  00d7  movwf   0x57                                   ; reg: 0x057
14d8:  08d7  movf    0x57, F                                ; reg: 0x057
14d9:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
14da:  2cdd  goto    0x04dd
14db:  3001  movlw   0x01
14dc:  00d7  movwf   0x57                                   ; reg: 0x057
14dd:  01d6  clrf    0x56                                   ; reg: 0x056
14de:  01d5  clrf    0x55                                   ; reg: 0x055
14df:  0851  movf    0x51, W                                ; reg: 0x051
14e0:  00d4  movwf   0x54                                   ; reg: 0x054
14e1:  0850  movf    0x50, W                                ; reg: 0x050
14e2:  00d3  movwf   0x53                                   ; reg: 0x053
14e3:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
14e4:  0855  movf    0x55, W                                ; reg: 0x055
14e5:  00d6  movwf   0x56                                   ; reg: 0x056
14e6:  0854  movf    0x54, W                                ; reg: 0x054
14e7:  00d5  movwf   0x55                                   ; reg: 0x055
14e8:  0853  movf    0x53, W                                ; reg: 0x053
14e9:  00d4  movwf   0x54                                   ; reg: 0x054
14ea:  01d3  clrf    0x53                                   ; reg: 0x053
14eb:  0dd4  rlf     0x54, F                                ; reg: 0x054
14ec:  0dd5  rlf     0x55, F                                ; reg: 0x055
14ed:  0dd6  rlf     0x56, F                                ; reg: 0x056
14ee:  0856  movf    0x56, W                                ; reg: 0x056
14ef:  00db  movwf   0x5b                                   ; reg: 0x05b
14f0:  0855  movf    0x55, W                                ; reg: 0x055
14f1:  00da  movwf   0x5a                                   ; reg: 0x05a
14f2:  0854  movf    0x54, W                                ; reg: 0x054
14f3:  00d9  movwf   0x59                                   ; reg: 0x059
14f4:  0853  movf    0x53, W                                ; reg: 0x053
14f5:  00d8  movwf   0x58                                   ; reg: 0x058
14f6:  01df  clrf    0x5f                                   ; reg: 0x05f
14f7:  01de  clrf    0x5e                                   ; reg: 0x05e
14f8:  01dd  clrf    0x5d                                   ; reg: 0x05d
14f9:  3064  movlw   0x64
14fa:  00dc  movwf   0x5c                                   ; reg: 0x05c
14fb:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
14fc:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
14fd:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
14fe:  20e7  call    function_039
14ff:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1500:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1501:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1502:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1503:  00d6  movwf   0x56                                   ; reg: 0x056
1504:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1505:  00d5  movwf   0x55                                   ; reg: 0x055
1506:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1507:  00d4  movwf   0x54                                   ; reg: 0x054
1508:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
1509:  00d3  movwf   0x53                                   ; reg: 0x053
150a:  0856  movf    0x56, W                                ; reg: 0x056
150b:  00db  movwf   0x5b                                   ; reg: 0x05b
150c:  0855  movf    0x55, W                                ; reg: 0x055
150d:  00da  movwf   0x5a                                   ; reg: 0x05a
150e:  0854  movf    0x54, W                                ; reg: 0x054
150f:  00d9  movwf   0x59                                   ; reg: 0x059
1510:  0853  movf    0x53, W                                ; reg: 0x053
1511:  00d8  movwf   0x58                                   ; reg: 0x058
1512:  01df  clrf    0x5f                                   ; reg: 0x05f
1513:  01de  clrf    0x5e                                   ; reg: 0x05e
1514:  01dd  clrf    0x5d                                   ; reg: 0x05d
1515:  0857  movf    0x57, W                                ; reg: 0x057
1516:  00dc  movwf   0x5c                                   ; reg: 0x05c
1517:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1518:  2c5a  goto    label_215

label_221:                                                  ; address: 0x1519

1519:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
151a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
151b:  00d6  movwf   0x56                                   ; reg: 0x056
151c:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
151d:  00d5  movwf   0x55                                   ; reg: 0x055
151e:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
151f:  00d4  movwf   0x54                                   ; reg: 0x054
1520:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
1521:  00d3  movwf   0x53                                   ; reg: 0x053
1522:  0854  movf    0x54, W                                ; reg: 0x054
1523:  00d3  movwf   0x53                                   ; reg: 0x053
1524:  0855  movf    0x55, W                                ; reg: 0x055
1525:  00d4  movwf   0x54                                   ; reg: 0x054
1526:  0856  movf    0x56, W                                ; reg: 0x056
1527:  00d5  movwf   0x55                                   ; reg: 0x055
1528:  01d6  clrf    0x56                                   ; reg: 0x056
1529:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
152a:  0cd6  rrf     0x56, F                                ; reg: 0x056
152b:  0cd5  rrf     0x55, F                                ; reg: 0x055
152c:  0cd4  rrf     0x54, F                                ; reg: 0x054
152d:  0cd3  rrf     0x53, F                                ; reg: 0x053
152e:  08d6  movf    0x56, F                                ; reg: 0x056
152f:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1530:  2d35  goto    label_222
1531:  0855  movf    0x55, W                                ; reg: 0x055
1532:  3c00  sublw   0x00
1533:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1534:  2d3a  goto    label_223

label_222:                                                  ; address: 0x1535

1535:  01d6  clrf    0x56                                   ; reg: 0x056
1536:  01d5  clrf    0x55                                   ; reg: 0x055
1537:  30ff  movlw   0xff
1538:  00d4  movwf   0x54                                   ; reg: 0x054
1539:  00d3  movwf   0x53                                   ; reg: 0x053

label_223:                                                  ; address: 0x153a

153a:  0854  movf    0x54, W                                ; reg: 0x054
153b:  00d1  movwf   0x51                                   ; reg: 0x051
153c:  0853  movf    0x53, W                                ; reg: 0x053
153d:  00d0  movwf   0x50                                   ; reg: 0x050
153e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
153f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1540:  0850  movf    0x50, W                                ; reg: 0x050
1541:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1542:  0851  movf    0x51, W                                ; reg: 0x051
1543:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
1544:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1545:  3400  retlw   0x00

function_055:                                               ; address: 0x1546

1546:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1547:  084e  movf    0x4e, W                                ; reg: 0x04e
1548:  00d1  movwf   0x51                                   ; reg: 0x051
1549:  084d  movf    0x4d, W                                ; reg: 0x04d
154a:  00d0  movwf   0x50                                   ; reg: 0x050
154b:  084f  movf    0x4f, W                                ; reg: 0x04f
154c:  00d2  movwf   0x52                                   ; reg: 0x052
154d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
154e:  24a0  call    function_054
154f:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1550:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1551:  00d1  movwf   0x51                                   ; reg: 0x051
1552:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1553:  00d0  movwf   0x50                                   ; reg: 0x050
1554:  0851  movf    0x51, W                                ; reg: 0x051
1555:  00d3  movwf   0x53                                   ; reg: 0x053
1556:  0850  movf    0x50, W                                ; reg: 0x050
1557:  00d2  movwf   0x52                                   ; reg: 0x052
1558:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1559:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
155a:  2624  call    function_026
155b:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
155c:  3400  retlw   0x00
155d:  087c  movf    (Common_RAM + 12), W                   ; reg: 0x07c
155e:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
155f:  206c  call    0x006c
1560:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1561:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1562:  00c8  movwf   0x48                                   ; reg: 0x048
1563:  01ce  clrf    0x4e                                   ; reg: 0x04e
1564:  0848  movf    0x48, W                                ; reg: 0x048
1565:  00cd  movwf   0x4d                                   ; reg: 0x04d
1566:  3058  movlw   0x58
1567:  00cf  movwf   0x4f                                   ; reg: 0x04f
1568:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1569:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
156a:  2477  call    0x0477
156b:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
156c:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
156d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
156e:  00ca  movwf   0x4a                                   ; reg: 0x04a
156f:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1570:  00c9  movwf   0x49                                   ; reg: 0x049
1571:  084a  movf    0x4a, W                                ; reg: 0x04a
1572:  00cf  movwf   0x4f                                   ; reg: 0x04f
1573:  0849  movf    0x49, W                                ; reg: 0x049
1574:  00ce  movwf   0x4e                                   ; reg: 0x04e
1575:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1576:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1577:  2546  call    0x0546
1578:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1579:  1afe  btfsc   (Common_RAM + 14), 0x5                 ; reg: 0x07e
157a:  2d9e  goto    0x059e
157b:  3001  movlw   0x01
157c:  077c  addwf   (Common_RAM + 12), W                   ; reg: 0x07c
157d:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
157e:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
157f:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
1580:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
1581:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1582:  00c9  movwf   0x49                                   ; reg: 0x049
1583:  0a49  incf    0x49, W                                ; reg: 0x049
1584:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1585:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1586:  2072  call    0x0072
1587:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1588:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1589:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
158a:  0849  movf    0x49, W                                ; reg: 0x049
158b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
158c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
158d:  2072  call    0x0072
158e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
158f:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1590:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1591:  024b  subwf   0x4b, W                                ; reg: 0x04b
1592:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1593:  2d9e  goto    0x059e
1594:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1595:  2d9a  goto    0x059a
1596:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1597:  024a  subwf   0x4a, W                                ; reg: 0x04a
1598:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1599:  2d9e  goto    0x059e
159a:  08fc  movf    (Common_RAM + 12), F                   ; reg: 0x07c
159b:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
159c:  2d9e  goto    0x059e
159d:  0afc  incf    (Common_RAM + 12), F                   ; reg: 0x07c
159e:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
159f:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
15a0:  2a67  goto    label_293

function_056:                                               ; address: 0x15a1

15a1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
15a2:  01cd  clrf    0x4d                                   ; reg: 0x04d
15a3:  01cc  clrf    0x4c                                   ; reg: 0x04c
15a4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
15a5:  0859  movf    0x59, W                                ; reg: 0x059
15a6:  3c09  sublw   0x09
15a7:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
15a8:  2dbd  goto    label_346
15a9:  0859  movf    0x59, W                                ; reg: 0x059
15aa:  3c0a  sublw   0x0a
15ab:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
15ac:  00cf  movwf   0x4f                                   ; reg: 0x04f
15ad:  01d7  clrf    0x57                                   ; reg: 0x057
15ae:  084f  movf    0x4f, W                                ; reg: 0x04f
15af:  00d6  movwf   0x56                                   ; reg: 0x056
15b0:  01d9  clrf    0x59                                   ; reg: 0x059
15b1:  302d  movlw   0x2d
15b2:  00d8  movwf   0x58                                   ; reg: 0x058
15b3:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
15b4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
15b5:  23b9  call    function_041
15b6:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
15b7:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
15b8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
15b9:  00cd  movwf   0x4d                                   ; reg: 0x04d
15ba:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
15bb:  00cc  movwf   0x4c                                   ; reg: 0x04c
15bc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
15bd:  3040  movlw   0x40
15be:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
15bf:  074c  addwf   0x4c, W                                ; reg: 0x04c
15c0:  00ce  movwf   0x4e                                   ; reg: 0x04e
15c1:  084d  movf    0x4d, W                                ; reg: 0x04d
15c2:  00cf  movwf   0x4f                                   ; reg: 0x04f
15c3:  300b  movlw   0x0b
15c4:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
15c5:  300c  movlw   0x0c
15c6:  07cf  addwf   0x4f, F                                ; reg: 0x04f
15c7:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
15c8:  1d2d  btfss   0x2d, 0x2                              ; reg: 0x02d
15c9:  2dcd  goto    0x05cd
15ca:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
15cb:  3000  movlw   0x00
15cc:  2dd0  goto    0x05d0
15cd:  3002  movlw   0x02
15ce:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
15cf:  301c  movlw   0x1c
15d0:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
15d1:  074e  addwf   0x4e, W                                ; reg: 0x04e
15d2:  00ca  movwf   0x4a                                   ; reg: 0x04a
15d3:  084f  movf    0x4f, W                                ; reg: 0x04f
15d4:  00cb  movwf   0x4b                                   ; reg: 0x04b
15d5:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
15d6:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
15d7:  0f7a  incfsz  (Common_RAM + 10), W                   ; reg: 0x07a
15d8:  07cb  addwf   0x4b, F                                ; reg: 0x04b
15d9:  084b  movf    0x4b, W                                ; reg: 0x04b
15da:  00d4  movwf   0x54                                   ; reg: 0x054
15db:  084a  movf    0x4a, W                                ; reg: 0x04a
15dc:  00d3  movwf   0x53                                   ; reg: 0x053
15dd:  305b  movlw   0x5b
15de:  00d5  movwf   0x55                                   ; reg: 0x055
15df:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
15e0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
15e1:  2422  call    0x0422
15e2:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
15e3:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
15e4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
15e5:  00cb  movwf   0x4b                                   ; reg: 0x04b
15e6:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
15e7:  00ca  movwf   0x4a                                   ; reg: 0x04a
15e8:  0848  movf    0x48, W                                ; reg: 0x048
15e9:  07ca  addwf   0x4a, F                                ; reg: 0x04a
15ea:  0849  movf    0x49, W                                ; reg: 0x049
15eb:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
15ec:  0f49  incfsz  0x49, W                                ; reg: 0x049
15ed:  07cb  addwf   0x4b, F                                ; reg: 0x04b
15ee:  084a  movf    0x4a, W                                ; reg: 0x04a
15ef:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
15f0:  084b  movf    0x4b, W                                ; reg: 0x04b
15f1:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
15f2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
15f3:  3400  retlw   0x00

label_224:                                                  ; address: 0x15f4

15f4:  2090  call    0x0090
15f5:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
15f6:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
15f7:  27df  call    function_049
15f8:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
15f9:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
15fa:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
15fb:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
15fc:  2b0e  goto    label_312

function_057:                                               ; address: 0x15fd

15fd:  084f  movf    0x4f, W                                ; reg: 0x04f
15fe:  39f7  andlw   0xf7
15ff:  3943  andlw   0x43
1600:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1601:  2e0c  goto    label_357
1602:  301c  movlw   0x1c
1603:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1604:  00cb  movwf   0x4b                                   ; reg: 0x04b
1605:  3020  movlw   0x20
1606:  00ca  movwf   0x4a                                   ; reg: 0x04a
1607:  3049  movlw   0x49
1608:  00cc  movwf   0x4c                                   ; reg: 0x04c
1609:  104d  bcf     0x4d, 0x0                              ; reg: 0x04d
160a:  2e23  goto    label_361
160b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
160c:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
160d:  0d7d  rlf     (Common_RAM + 13), W                   ; reg: 0x07d
160e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
160f:  00ce  movwf   0x4e                                   ; reg: 0x04e
1610:  0a4e  incf    0x4e, W                                ; reg: 0x04e
1611:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1612:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1613:  2060  call    function_037
1614:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1615:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1616:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1617:  084e  movf    0x4e, W                                ; reg: 0x04e
1618:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1619:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
161a:  2060  call    0x0060
161b:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
161c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
161d:  00ca  movwf   0x4a                                   ; reg: 0x04a
161e:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
161f:  00cb  movwf   0x4b                                   ; reg: 0x04b
1620:  3059  movlw   0x59
1621:  00cc  movwf   0x4c                                   ; reg: 0x04c
1622:  144d  bsf     0x4d, 0x0                              ; reg: 0x04d
1623:  084b  movf    0x4b, W                                ; reg: 0x04b
1624:  00d1  movwf   0x51                                   ; reg: 0x051
1625:  084a  movf    0x4a, W                                ; reg: 0x04a
1626:  00d0  movwf   0x50                                   ; reg: 0x050
1627:  084c  movf    0x4c, W                                ; reg: 0x04c
1628:  00d2  movwf   0x52                                   ; reg: 0x052
1629:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
162a:  24a0  call    0x04a0
162b:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
162c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
162d:  00c9  movwf   0x49                                   ; reg: 0x049
162e:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
162f:  00c8  movwf   0x48                                   ; reg: 0x048
1630:  1c4d  btfss   0x4d, 0x0                              ; reg: 0x04d
1631:  2e42  goto    0x0642
1632:  0849  movf    0x49, W                                ; reg: 0x049
1633:  00db  movwf   0x5b                                   ; reg: 0x05b
1634:  0848  movf    0x48, W                                ; reg: 0x048
1635:  00da  movwf   0x5a                                   ; reg: 0x05a
1636:  01dd  clrf    0x5d                                   ; reg: 0x05d
1637:  30aa  movlw   0xaa
1638:  00dc  movwf   0x5c                                   ; reg: 0x05c
1639:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
163a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
163b:  23e7  call    0x03e7
163c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
163d:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
163e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
163f:  00c9  movwf   0x49                                   ; reg: 0x049
1640:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1641:  00c8  movwf   0x48                                   ; reg: 0x048
1642:  0849  movf    0x49, W                                ; reg: 0x049
1643:  00d3  movwf   0x53                                   ; reg: 0x053
1644:  0848  movf    0x48, W                                ; reg: 0x048
1645:  00d2  movwf   0x52                                   ; reg: 0x052
1646:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1647:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1648:  2624  call    0x0624
1649:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
164a:  3400  retlw   0x00
164b:  084c  movf    0x4c, W                                ; reg: 0x04c
164c:  3907  andlw   0x07
164d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
164e:  00c8  movwf   0x48                                   ; reg: 0x048
164f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1650:  1e4c  btfss   0x4c, 0x4                              ; reg: 0x04c
1651:  2e5c  goto    0x065c
1652:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1653:  08c8  movf    0x48, F                                ; reg: 0x048
1654:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1655:  2e5b  goto    0x065b
1656:  0875  movf    (Common_RAM + 5), W                    ; reg: 0x075
1657:  0276  subwf   (Common_RAM + 6), W                    ; reg: 0x076
1658:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1659:  2e5b  goto    0x065b
165a:  03c8  decf    0x48, F                                ; reg: 0x048
165b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
165c:  08ed  movf    0x6d, F                                ; reg: 0x06d
165d:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
165e:  2e7f  goto    0x067f
165f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1660:  0848  movf    0x48, W                                ; reg: 0x048
1661:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1662:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1663:  2045  call    0x0045
1664:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1665:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1666:  00c9  movwf   0x49                                   ; reg: 0x049
1667:  1ba2  btfsc   0x22, 0x7                              ; reg: 0x022
1668:  2e74  goto    0x0674
1669:  0822  movf    0x22, W                                ; reg: 0x022
166a:  3c00  sublw   0x00
166b:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
166c:  2e74  goto    0x0674
166d:  0c22  rrf     0x22, W                                ; reg: 0x022
166e:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
166f:  0cf7  rrf     (Common_RAM + 7), F                    ; reg: 0x077
1670:  303f  movlw   0x3f
1671:  05f7  andwf   (Common_RAM + 7), F                    ; reg: 0x077
1672:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
1673:  2e75  goto    0x0675
1674:  3000  movlw   0x00
1675:  0749  addwf   0x49, W                                ; reg: 0x049
1676:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1677:  0257  subwf   0x57, W                                ; reg: 0x057
1678:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1679:  2e7c  goto    0x067c
167a:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
167b:  2e7f  goto    0x067f
167c:  3001  movlw   0x01
167d:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
167e:  2e81  goto    0x0681
167f:  3000  movlw   0x00
1680:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1681:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1682:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1683:  2c45  goto    label_327

function_058:                                               ; address: 0x1684

1684:  1c7e  btfss   (Common_RAM + 14), 0x0                 ; reg: 0x07e
1685:  2ea5  goto    0x06a5
1686:  3063  movlw   0x63
1687:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1688:  00da  movwf   0x5a                                   ; reg: 0x05a
1689:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
168a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
168b:  23d0  call    function_042
168c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
168d:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
168e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
168f:  00c8  movwf   0x48                                   ; reg: 0x048
1690:  08c8  movf    0x48, F                                ; reg: 0x048
1691:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1692:  2e99  goto    0x0699
1693:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1694:  084c  movf    0x4c, W                                ; reg: 0x04c
1695:  3907  andlw   0x07
1696:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1697:  00c8  movwf   0x48                                   ; reg: 0x048
1698:  2e9a  goto    0x069a
1699:  03c8  decf    0x48, F                                ; reg: 0x048
169a:  0848  movf    0x48, W                                ; reg: 0x048
169b:  3c07  sublw   0x07
169c:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
169d:  2ea0  goto    0x06a0
169e:  3003  movlw   0x03
169f:  00c8  movwf   0x48                                   ; reg: 0x048
16a0:  0848  movf    0x48, W                                ; reg: 0x048
16a1:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
16a2:  2ea9  goto    0x06a9
16a3:  2ea9  goto    0x06a9
16a4:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
16a5:  3003  movlw   0x03
16a6:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
16a7:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
16a8:  2ea9  goto    0x06a9
16a9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
16aa:  3400  retlw   0x00

function_059:                                               ; address: 0x16ab

16ab:  30ff  movlw   0xff
16ac:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
16ad:  00ca  movwf   0x4a                                   ; reg: 0x04a
16ae:  01c9  clrf    0x49                                   ; reg: 0x049
16af:  01c8  clrf    0x48                                   ; reg: 0x048
16b0:  0848  movf    0x48, W                                ; reg: 0x048
16b1:  3c07  sublw   0x07
16b2:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
16b3:  2ec7  goto    0x06c7
16b4:  3063  movlw   0x63
16b5:  0748  addwf   0x48, W                                ; reg: 0x048
16b6:  0084  movwf   FSR                                    ; reg: 0x004
16b7:  0800  movf    INDF, W                                ; reg: 0x000
16b8:  00cb  movwf   0x4b                                   ; reg: 0x04b
16b9:  084a  movf    0x4a, W                                ; reg: 0x04a
16ba:  024b  subwf   0x4b, W                                ; reg: 0x04b
16bb:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
16bc:  2ebf  goto    0x06bf
16bd:  084b  movf    0x4b, W                                ; reg: 0x04b
16be:  00ca  movwf   0x4a                                   ; reg: 0x04a
16bf:  084b  movf    0x4b, W                                ; reg: 0x04b
16c0:  0249  subwf   0x49, W                                ; reg: 0x049
16c1:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
16c2:  2ec5  goto    0x06c5
16c3:  084b  movf    0x4b, W                                ; reg: 0x04b
16c4:  00c9  movwf   0x49                                   ; reg: 0x049
16c5:  0ac8  incf    0x48, F                                ; reg: 0x048
16c6:  2eb0  goto    0x06b0
16c7:  084a  movf    0x4a, W                                ; reg: 0x04a
16c8:  02c9  subwf   0x49, F                                ; reg: 0x049
16c9:  0876  movf    (Common_RAM + 6), W                    ; reg: 0x076
16ca:  00c8  movwf   0x48                                   ; reg: 0x048
16cb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
16cc:  1c50  btfss   0x50, 0x0                              ; reg: 0x050
16cd:  2ed3  goto    0x06d3
16ce:  30d0  movlw   0xd0
16cf:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
16d0:  3002  movlw   0x02
16d1:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
16d2:  2f17  goto    0x0717
16d3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
16d4:  0849  movf    0x49, W                                ; reg: 0x049
16d5:  3c02  sublw   0x02
16d6:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
16d7:  2ee0  goto    0x06e0
16d8:  3010  movlw   0x10
16d9:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
16da:  300e  movlw   0x0e
16db:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
16dc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
16dd:  2f17  goto    0x0717
16de:  2f17  goto    0x0717
16df:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
16e0:  0875  movf    (Common_RAM + 5), W                    ; reg: 0x075
16e1:  0276  subwf   (Common_RAM + 6), W                    ; reg: 0x076
16e2:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
16e3:  2f11  goto    0x0711
16e4:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
16e5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
16e6:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
16e7:  2113  call    function_040
16e8:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
16e9:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
16ea:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
16eb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
16ec:  00cd  movwf   0x4d                                   ; reg: 0x04d
16ed:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
16ee:  00cc  movwf   0x4c                                   ; reg: 0x04c
16ef:  0c4d  rrf     0x4d, W                                ; reg: 0x04d
16f0:  00cf  movwf   0x4f                                   ; reg: 0x04f
16f1:  0c4c  rrf     0x4c, W                                ; reg: 0x04c
16f2:  00ce  movwf   0x4e                                   ; reg: 0x04e
16f3:  0ccf  rrf     0x4f, F                                ; reg: 0x04f
16f4:  0cce  rrf     0x4e, F                                ; reg: 0x04e
16f5:  0ccf  rrf     0x4f, F                                ; reg: 0x04f
16f6:  0cce  rrf     0x4e, F                                ; reg: 0x04e
16f7:  301f  movlw   0x1f
16f8:  05cf  andwf   0x4f, F                                ; reg: 0x04f
16f9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
16fa:  083a  movf    0x3a, W                                ; reg: 0x03a
16fb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
16fc:  024f  subwf   0x4f, W                                ; reg: 0x04f
16fd:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
16fe:  2f11  goto    label_227
16ff:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1700:  2f09  goto    label_226
1701:  084e  movf    0x4e, W                                ; reg: 0x04e
1702:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1703:  0239  subwf   0x39, W                                ; reg: 0x039
1704:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1705:  2f08  goto    label_225
1706:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1707:  2f11  goto    label_227

label_225:                                                  ; address: 0x1708

1708:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_226:                                                  ; address: 0x1709

1709:  3070  movlw   0x70
170a:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
170b:  3008  movlw   0x08
170c:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
170d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
170e:  2f17  goto    label_228
170f:  2f17  goto    label_228
1710:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_227:                                                  ; address: 0x1711

1711:  3038  movlw   0x38
1712:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1713:  3004  movlw   0x04
1714:  00f9  movwf   (Common_RAM + 9)                       ; reg: 0x079
1715:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1716:  2f17  goto    label_228

label_228:                                                  ; address: 0x1717

1717:  3400  retlw   0x00
1718:  086b  movf    0x6b, W                                ; reg: 0x06b
1719:  0257  subwf   0x57, W                                ; reg: 0x057
171a:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
171b:  2f1e  goto    label_229
171c:  0857  movf    0x57, W                                ; reg: 0x057
171d:  2f1f  goto    label_230

label_229:                                                  ; address: 0x171e

171e:  086b  movf    0x6b, W                                ; reg: 0x06b

label_230:                                                  ; address: 0x171f

171f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1720:  00cb  movwf   0x4b                                   ; reg: 0x04b
1721:  01c8  clrf    0x48                                   ; reg: 0x048
1722:  3008  movlw   0x08
1723:  00d3  movwf   0x53                                   ; reg: 0x053
1724:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1725:  086c  movf    0x6c, W                                ; reg: 0x06c
1726:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1727:  00d4  movwf   0x54                                   ; reg: 0x054
1728:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1729:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
172a:  22bc  call    function_014
172b:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
172c:  3009  movlw   0x09
172d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
172e:  00d3  movwf   0x53                                   ; reg: 0x053
172f:  084b  movf    0x4b, W                                ; reg: 0x04b
1730:  00d4  movwf   0x54                                   ; reg: 0x054
1731:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1732:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1733:  22bc  call    0x02bc
1734:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1735:  0876  movf    (Common_RAM + 6), W                    ; reg: 0x076
1736:  0275  subwf   (Common_RAM + 5), W                    ; reg: 0x075
1737:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1738:  2f3b  goto    0x073b
1739:  0acc  incf    0x4c, F                                ; reg: 0x04c
173a:  0af5  incf    (Common_RAM + 5), F                    ; reg: 0x075
173b:  0875  movf    (Common_RAM + 5), W                    ; reg: 0x075
173c:  0276  subwf   (Common_RAM + 6), W                    ; reg: 0x076
173d:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
173e:  2f71  goto    0x0771
173f:  03cc  decf    0x4c, F                                ; reg: 0x04c
1740:  03f5  decf    (Common_RAM + 5), F                    ; reg: 0x075
1741:  0862  movf    0x62, W                                ; reg: 0x062
1742:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1743:  00cd  movwf   0x4d                                   ; reg: 0x04d
1744:  08cd  movf    0x4d, F                                ; reg: 0x04d
1745:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1746:  2f49  goto    0x0749
1747:  3008  movlw   0x08
1748:  00cd  movwf   0x4d                                   ; reg: 0x04d
1749:  03cd  decf    0x4d, F                                ; reg: 0x04d
174a:  084d  movf    0x4d, W                                ; reg: 0x04d
174b:  00cc  movwf   0x4c                                   ; reg: 0x04c
174c:  08cc  movf    0x4c, F                                ; reg: 0x04c
174d:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
174e:  2f51  goto    0x0751
174f:  3008  movlw   0x08
1750:  00cc  movwf   0x4c                                   ; reg: 0x04c
1751:  03cc  decf    0x4c, F                                ; reg: 0x04c
1752:  3063  movlw   0x63
1753:  074c  addwf   0x4c, W                                ; reg: 0x04c
1754:  0084  movwf   FSR                                    ; reg: 0x004
1755:  0800  movf    INDF, W                                ; reg: 0x000
1756:  00cf  movwf   0x4f                                   ; reg: 0x04f
1757:  3063  movlw   0x63
1758:  074d  addwf   0x4d, W                                ; reg: 0x04d
1759:  0084  movwf   FSR                                    ; reg: 0x004
175a:  0800  movf    INDF, W                                ; reg: 0x000
175b:  00d0  movwf   0x50                                   ; reg: 0x050
175c:  084f  movf    0x4f, W                                ; reg: 0x04f
175d:  0250  subwf   0x50, W                                ; reg: 0x050
175e:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
175f:  2f70  goto    0x0770
1760:  0850  movf    0x50, W                                ; reg: 0x050
1761:  024f  subwf   0x4f, W                                ; reg: 0x04f
1762:  00c8  movwf   0x48                                   ; reg: 0x048
1763:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
1764:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
1765:  3c07  sublw   0x07
1766:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1767:  2f70  goto    0x0770
1768:  3063  movlw   0x63
1769:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
176a:  0084  movwf   FSR                                    ; reg: 0x004
176b:  0848  movf    0x48, W                                ; reg: 0x048
176c:  0200  subwf   INDF, W                                ; reg: 0x000
176d:  0080  movwf   INDF                                   ; reg: 0x000
176e:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
176f:  2f64  goto    0x0764
1770:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1771:  086c  movf    0x6c, W                                ; reg: 0x06c
1772:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1773:  024b  subwf   0x4b, W                                ; reg: 0x04b
1774:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1775:  2fbb  goto    0x07bb
1776:  084b  movf    0x4b, W                                ; reg: 0x04b
1777:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1778:  026c  subwf   0x6c, W                                ; reg: 0x06c
1779:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
177a:  00c8  movwf   0x48                                   ; reg: 0x048
177b:  01ca  clrf    0x4a                                   ; reg: 0x04a
177c:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
177d:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
177e:  3c07  sublw   0x07
177f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1780:  2f8e  goto    0x078e
1781:  3063  movlw   0x63
1782:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
1783:  0084  movwf   FSR                                    ; reg: 0x004
1784:  0800  movf    INDF, W                                ; reg: 0x000
1785:  00cf  movwf   0x4f                                   ; reg: 0x04f
1786:  084a  movf    0x4a, W                                ; reg: 0x04a
1787:  024f  subwf   0x4f, W                                ; reg: 0x04f
1788:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1789:  2f8c  goto    0x078c
178a:  084f  movf    0x4f, W                                ; reg: 0x04f
178b:  00ca  movwf   0x4a                                   ; reg: 0x04a
178c:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
178d:  2f7d  goto    0x077d
178e:  084b  movf    0x4b, W                                ; reg: 0x04b
178f:  024a  subwf   0x4a, W                                ; reg: 0x04a
1790:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1791:  2f94  goto    0x0794
1792:  01c8  clrf    0x48                                   ; reg: 0x048
1793:  2f9d  goto    0x079d
1794:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1795:  086c  movf    0x6c, W                                ; reg: 0x06c
1796:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1797:  024a  subwf   0x4a, W                                ; reg: 0x04a
1798:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1799:  2f9d  goto    0x079d
179a:  084b  movf    0x4b, W                                ; reg: 0x04b
179b:  024a  subwf   0x4a, W                                ; reg: 0x04a
179c:  00c8  movwf   0x48                                   ; reg: 0x048
179d:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
179e:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
179f:  3c07  sublw   0x07
17a0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
17a1:  2fb1  goto    0x07b1
17a2:  3063  movlw   0x63
17a3:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
17a4:  0084  movwf   FSR                                    ; reg: 0x004
17a5:  0800  movf    INDF, W                                ; reg: 0x000
17a6:  0248  subwf   0x48, W                                ; reg: 0x048
17a7:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
17a8:  2faf  goto    0x07af
17a9:  3063  movlw   0x63
17aa:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
17ab:  0084  movwf   FSR                                    ; reg: 0x004
17ac:  0848  movf    0x48, W                                ; reg: 0x048
17ad:  0200  subwf   INDF, W                                ; reg: 0x000
17ae:  0080  movwf   INDF                                   ; reg: 0x000
17af:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
17b0:  2f9e  goto    0x079e
17b1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
17b2:  086b  movf    0x6b, W                                ; reg: 0x06b
17b3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
17b4:  0248  subwf   0x48, W                                ; reg: 0x048
17b5:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
17b6:  2fbb  goto    0x07bb
17b7:  0848  movf    0x48, W                                ; reg: 0x048
17b8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
17b9:  02eb  subwf   0x6b, F                                ; reg: 0x06b
17ba:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
17bb:  084b  movf    0x4b, W                                ; reg: 0x04b
17bc:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
17bd:  026c  subwf   0x6c, W                                ; reg: 0x06c
17be:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
17bf:  2fe5  goto    0x07e5
17c0:  086c  movf    0x6c, W                                ; reg: 0x06c
17c1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
17c2:  024b  subwf   0x4b, W                                ; reg: 0x04b
17c3:  00c8  movwf   0x48                                   ; reg: 0x048
17c4:  01f4  clrf    (Common_RAM + 4)                       ; reg: 0x074
17c5:  0874  movf    (Common_RAM + 4), W                    ; reg: 0x074
17c6:  3c07  sublw   0x07
17c7:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
17c8:  2fdb  goto    0x07db
17c9:  3063  movlw   0x63
17ca:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
17cb:  0084  movwf   FSR                                    ; reg: 0x004
17cc:  0800  movf    INDF, W                                ; reg: 0x000
17cd:  00d1  movwf   0x51                                   ; reg: 0x051
17ce:  0848  movf    0x48, W                                ; reg: 0x048
17cf:  3cff  sublw   0xff
17d0:  0251  subwf   0x51, W                                ; reg: 0x051
17d1:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
17d2:  2fd9  goto    0x07d9
17d3:  3063  movlw   0x63
17d4:  0774  addwf   (Common_RAM + 4), W                    ; reg: 0x074
17d5:  0084  movwf   FSR                                    ; reg: 0x004
17d6:  0848  movf    0x48, W                                ; reg: 0x048
17d7:  0700  addwf   INDF, W                                ; reg: 0x000
17d8:  0080  movwf   INDF                                   ; reg: 0x000
17d9:  0af4  incf    (Common_RAM + 4), F                    ; reg: 0x074
17da:  2fc5  goto    0x07c5
17db:  0848  movf    0x48, W                                ; reg: 0x048
17dc:  3cff  sublw   0xff
17dd:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
17de:  026b  subwf   0x6b, W                                ; reg: 0x06b
17df:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
17e0:  2fe5  goto    0x07e5
17e1:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
17e2:  0848  movf    0x48, W                                ; reg: 0x048
17e3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
17e4:  07eb  addwf   0x6b, F                                ; reg: 0x06b
17e5:  300a  movlw   0x0a
17e6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
17e7:  00d3  movwf   0x53                                   ; reg: 0x053
17e8:  0848  movf    0x48, W                                ; reg: 0x048
17e9:  00d4  movwf   0x54                                   ; reg: 0x054
17ea:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
17eb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
17ec:  22bc  call    0x02bc
17ed:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
17ee:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

function_060:                                               ; address: 0x17ef

17ef:  084b  movf    0x4b, W                                ; reg: 0x04b
17f0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
17f1:  00ec  movwf   0x6c                                   ; reg: 0x06c
17f2:  3400  retlw   0x00

function_061:                                               ; address: 0x1800

1800:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1801:  084f  movf    0x4f, W                                ; reg: 0x04f
1802:  3cc2  sublw   0xc2
1803:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1804:  2807  goto    0x0007
1805:  30c3  movlw   0xc3
1806:  00cf  movwf   0x4f                                   ; reg: 0x04f
1807:  01db  clrf    0x5b                                   ; reg: 0x05b
1808:  084f  movf    0x4f, W                                ; reg: 0x04f
1809:  00da  movwf   0x5a                                   ; reg: 0x05a
180a:  01dd  clrf    0x5d                                   ; reg: 0x05d
180b:  30a4  movlw   0xa4
180c:  00dc  movwf   0x5c                                   ; reg: 0x05c
180d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
180e:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
180f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1810:  23e7  call    function_018
1811:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1812:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1813:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1814:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1815:  00cf  movwf   0x4f                                   ; reg: 0x04f
1816:  084e  movf    0x4e, W                                ; reg: 0x04e
1817:  00db  movwf   0x5b                                   ; reg: 0x05b
1818:  084d  movf    0x4d, W                                ; reg: 0x04d
1819:  00da  movwf   0x5a                                   ; reg: 0x05a
181a:  01dd  clrf    0x5d                                   ; reg: 0x05d
181b:  084f  movf    0x4f, W                                ; reg: 0x04f
181c:  00dc  movwf   0x5c                                   ; reg: 0x05c
181d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
181e:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
181f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1820:  23e7  call    function_018
1821:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1822:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1823:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1824:  3400  retlw   0x00

; >>> RE NOTES @ 0x1825
; MAIN STARTUP. Clears/initializes PIC peripherals and runtime state.
; <<<
1825:  0184  clrf    FSR                                    ; reg: 0x004
1826:  301f  movlw   0x1f
1827:  0583  andwf   STATUS, F                              ; reg: 0x003
1828:  3020  movlw   0x20

; >>> RE NOTES @ 0x1829
; BANK NOTE: RP0=1 here. Address 0x99 is SPBRG, NOT TXREG. Firmware writes SPBRG=0x20.
; <<<
1829:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
182a:  0099  movwf   TXREG                                  ; reg: 0x019
182b:  3026  movlw   0x26

; >>> RE NOTES @ 0x182C
; BANK NOTE: RP0=1 here. Address 0x98 is TXSTA, NOT RCSTA. Firmware writes TXSTA=0x26 (async TX enabled, BRGH=1).
; <<<
182c:  0098  movwf   RCSTA                                  ; reg: 0x018
182d:  3090  movlw   0x90
182e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

; >>> RE NOTES @ 0x182F
; RP0=0 here: RCSTA=0x90 (SPEN=1, CREN=1), enabling asynchronous serial receive.
; <<<
182f:  0098  movwf   RCSTA                                  ; reg: 0x018
1830:  3018  movlw   0x18
1831:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1832:  0093  movwf   SSPBUF                                 ; reg: 0x013
1833:  3028  movlw   0x28
1834:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1835:  0094  movwf   SSPCON                                 ; reg: 0x014
1836:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1837:  1794  bsf     SSPCON, WCOL                           ; reg: 0x014, bit: 7
1838:  1314  bcf     SSPCON, SSPOV                          ; reg: 0x014, bit: 6
1839:  141f  bsf     ADCON0, ADON                           ; reg: 0x01f, bit: 0
183a:  149f  bsf     ADCON0, 0x1                            ; reg: 0x01f
183b:  151f  bsf     ADCON0, GO                             ; reg: 0x01f, bit: 2
183c:  119f  bcf     ADCON0, CHS0                           ; reg: 0x01f, bit: 3
183d:  3007  movlw   0x07
183e:  009c  movwf   CCPR2H                                 ; reg: 0x01c
183f:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1840:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1841:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1842:  2a47  goto    label_060

label_231:                                                  ; address: 0x1843

1843:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1844:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1845:  01b2  clrf    0x32                                   ; reg: 0x032
1846:  01b1  clrf    0x31                                   ; reg: 0x031
1847:  01cc  clrf    0x4c                                   ; reg: 0x04c
1848:  01ba  clrf    0x3a                                   ; reg: 0x03a
1849:  01b9  clrf    0x39                                   ; reg: 0x039
184a:  01cf  clrf    0x4f                                   ; reg: 0x04f
184b:  01de  clrf    0x5e                                   ; reg: 0x05e
184c:  01df  clrf    0x5f                                   ; reg: 0x05f
184d:  01e0  clrf    0x60                                   ; reg: 0x060
184e:  01ef  clrf    0x6f                                   ; reg: 0x06f
184f:  01d0  clrf    0x50                                   ; reg: 0x050
1850:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1851:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1852:  2255  call    function_009
1853:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1854:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1855:  01fe  clrf    (Common_RAM + 14)                      ; reg: 0x07e
1856:  01f5  clrf    (Common_RAM + 5)                       ; reg: 0x075

label_232:                                                  ; address: 0x1857

1857:  0875  movf    (Common_RAM + 5), W                    ; reg: 0x075
1858:  3c06  sublw   0x06
1859:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
185a:  2862  goto    label_233
185b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
185c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
185d:  22f6  call    function_015
185e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
185f:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1860:  0af5  incf    (Common_RAM + 5), F                    ; reg: 0x075
1861:  2857  goto    label_232

label_233:                                                  ; address: 0x1862

1862:  3001  movlw   0x01
1863:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1864:  00c8  movwf   0x48                                   ; reg: 0x048
1865:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1866:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1867:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1868:  25b1  call    function_023
1869:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
186a:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
186b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
186c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
186d:  2e17  goto    label_072

label_234:                                                  ; address: 0x186e

186e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
186f:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1870:  3005  movlw   0x05
1871:  00c5  movwf   0x45                                   ; reg: 0x045
1872:  3014  movlw   0x14
1873:  00c4  movwf   0x44                                   ; reg: 0x044
1874:  01c7  clrf    0x47                                   ; reg: 0x047
1875:  01c6  clrf    0x46                                   ; reg: 0x046
1876:  301c  movlw   0x1c
1877:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1878:  00d3  movwf   0x53                                   ; reg: 0x053
1879:  3020  movlw   0x20
187a:  00d2  movwf   0x52                                   ; reg: 0x052
187b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
187c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
187d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
187e:  2624  call    function_026
187f:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1880:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1881:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1882:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1883:  26a9  call    function_027
1884:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1885:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1886:  1ec3  btfss   0x43, 0x5                              ; reg: 0x043
1887:  288a  goto    label_235
1888:  3021  movlw   0x21
1889:  288b  goto    label_236

label_235:                                                  ; address: 0x188a

188a:  3001  movlw   0x01

label_236:                                                  ; address: 0x188b

188b:  00c3  movwf   0x43                                   ; reg: 0x043
188c:  16c3  bsf     0x43, 0x5                              ; reg: 0x043
188d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
188e:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
188f:  2753  call    function_031
1890:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1891:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1892:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1893:  01c0  clrf    0x40                                   ; reg: 0x040
1894:  01c1  clrf    0x41                                   ; reg: 0x041
1895:  168c  bsf     PIR1, RCIF                             ; reg: 0x00c, bit: 5
1896:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5

; >>> RE NOTES @ 0x1897
; UART receiver explicitly enabled again: RCSTA.SPEN=1, CREN=1.
; <<<
1897:  1798  bsf     RCSTA, SPEN                            ; reg: 0x018, bit: 7
1898:  1618  bsf     RCSTA, CREN                            ; reg: 0x018, bit: 4

label_237:                                                  ; address: 0x1899

1899:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
189a:  2000  call    function_036
189b:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
189c:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
189d:  2c1b  goto    0x041b

label_238:                                                  ; address: 0x189e

189e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
189f:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
18a0:  24c3  call    0x04c3
18a1:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
18a2:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
18a3:  2d02  goto    0x0502

label_239:                                                  ; address: 0x18a4

18a4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
18a5:  1cf0  btfss   Common_RAM, 0x1                        ; reg: 0x070
18a6:  28c0  goto    0x00c0
18a7:  0af0  incf    Common_RAM, F                          ; reg: 0x070
18a8:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
18a9:  08c2  movf    0x42, F                                ; reg: 0x042
18aa:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
18ab:  28be  goto    0x00be
18ac:  0842  movf    0x42, W                                ; reg: 0x042
18ad:  3c79  sublw   0x79
18ae:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
18af:  28b7  goto    0x00b7
18b0:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
18b1:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
18b2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
18b3:  228d  call    function_012
18b4:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
18b5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
18b6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
18b7:  03c2  decf    0x42, F                                ; reg: 0x042
18b8:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
18b9:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
18ba:  2da6  goto    label_134

label_240:                                                  ; address: 0x18bb

18bb:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
18bc:  28c0  goto    label_241
18bd:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
18be:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
18bf:  11d1  bcf     0x51, 0x3                              ; reg: 0x051

label_241:                                                  ; address: 0x18c0

18c0:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
18c1:  2f27  goto    label_135

label_242:                                                  ; address: 0x18c2

18c2:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
18c3:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
18c4:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
18c5:  28d5  goto    label_245
18c6:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
18c7:  28e0  goto    label_156

label_243:                                                  ; address: 0x18c8

18c8:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
18c9:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
18ca:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
18cb:  28d5  goto    label_245
18cc:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
18cd:  0842  movf    0x42, W                                ; reg: 0x042
18ce:  3c77  sublw   0x77
18cf:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
18d0:  28d3  goto    label_244
18d1:  3078  movlw   0x78
18d2:  00c2  movwf   0x42                                   ; reg: 0x042

label_244:                                                  ; address: 0x18d3

18d3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
18d4:  2899  goto    label_237

label_245:                                                  ; address: 0x18d5

18d5:  0870  movf    Common_RAM, W                          ; reg: 0x070
18d6:  3cf0  sublw   0xf0
18d7:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
18d8:  28df  goto    label_246
18d9:  01f0  clrf    Common_RAM                             ; reg: 0x070
18da:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
18db:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
18dc:  2753  call    function_031
18dd:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
18de:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_246:                                                  ; address: 0x18df

18df:  1dd1  btfss   0x51, 0x3                              ; reg: 0x051
18e0:  28e2  goto    label_247
18e1:  2899  goto    label_237

label_247:                                                  ; address: 0x18e2

18e2:  1fdd  btfss   0x5d, 0x7                              ; reg: 0x05d
18e3:  28f2  goto    label_248
18e4:  1f5d  btfss   0x5d, 0x6                              ; reg: 0x05d
18e5:  28f2  goto    label_248
18e6:  13dd  bcf     0x5d, 0x7                              ; reg: 0x05d
18e7:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
18e8:  2381  call    function_051
18e9:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
18ea:  084c  movf    0x4c, W                                ; reg: 0x04c
18eb:  3c2f  sublw   0x2f
18ec:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
18ed:  28ef  goto    0x00ef
18ee:  2922  goto    0x0122
18ef:  1db0  btfss   0x30, 0x3                              ; reg: 0x030
18f0:  28f2  goto    0x00f2
18f1:  2922  goto    0x0122

label_248:                                                  ; address: 0x18f2

18f2:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
18f3:  2b91  goto    0x0391

label_249:                                                  ; address: 0x18f4

18f4:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
18f5:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
18f6:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
18f7:  28f9  goto    0x00f9
18f8:  2922  goto    0x0122
18f9:  084c  movf    0x4c, W                                ; reg: 0x04c
18fa:  3970  andlw   0x70
18fb:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
18fc:  2913  goto    0x0113
18fd:  3a10  xorlw   0x10
18fe:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
18ff:  2950  goto    0x0150
1900:  3a30  xorlw   0x30
1901:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1902:  29a7  goto    0x01a7
1903:  3a10  xorlw   0x10
1904:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1905:  2a27  goto    0x0227
1906:  3a70  xorlw   0x70
1907:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1908:  2c00  goto    0x0400
1909:  3a10  xorlw   0x10
190a:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
190b:  2c00  goto    0x0400
190c:  3a30  xorlw   0x30
190d:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
190e:  2d3e  goto    0x053e
190f:  3a10  xorlw   0x10

label_250:                                                  ; address: 0x1910

1910:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1911:  2e5d  goto    0x065d
1912:  2e5d  goto    0x065d

function_062:                                               ; address: 0x1913

1913:  08cb  movf    0x4b, F                                ; reg: 0x04b
1914:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1915:  291a  goto    0x011a

label_251:                                                  ; address: 0x1916

1916:  084a  movf    0x4a, W                                ; reg: 0x04a
1917:  3c0b  sublw   0x0b
1918:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1919:  2e5d  goto    0x065d
191a:  0857  movf    0x57, W                                ; reg: 0x057
191b:  3c09  sublw   0x09
191c:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
191d:  291f  goto    0x011f
191e:  144f  bsf     0x4f, 0x0                              ; reg: 0x04f
191f:  2922  goto    0x0122
1920:  2e5d  goto    0x065d

label_252:                                                  ; address: 0x1921

1921:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f

label_253:                                                  ; address: 0x1922

1922:  1b5d  btfsc   0x5d, 0x6                              ; reg: 0x05d
1923:  292b  goto    0x012b
1924:  1930  btfsc   0x30, 0x2                              ; reg: 0x030
1925:  292b  goto    0x012b
1926:  084f  movf    0x4f, W                                ; reg: 0x04f
1927:  39f7  andlw   0xf7
1928:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1929:  292b  goto    0x012b
192a:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
192b:  135d  bcf     0x5d, 0x6                              ; reg: 0x05d
192c:  1ed0  btfss   0x50, 0x5                              ; reg: 0x050
192d:  2932  goto    0x0132
192e:  3007  movlw   0x07
192f:  05cc  andwf   0x4c, F                                ; reg: 0x04c
1930:  164c  bsf     0x4c, 0x4                              ; reg: 0x04c
1931:  2934  goto    0x0134
1932:  3010  movlw   0x10
1933:  00cc  movwf   0x4c                                   ; reg: 0x04c
1934:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1935:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1936:  228d  call    function_012
1937:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1938:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1939:  1fad  btfss   0x2d, 0x7                              ; reg: 0x02d
193a:  2941  goto    label_254
193b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
193c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
193d:  226a  call    function_010
193e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
193f:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1940:  2944  goto    label_255

label_254:                                                  ; address: 0x1941

1941:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1942:  27d3  call    function_048
1943:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a

label_255:                                                  ; address: 0x1944

1944:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1945:  2bde  goto    label_200

label_256:                                                  ; address: 0x1946

1946:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1947:  16c3  bsf     0x43, 0x5                              ; reg: 0x043
1948:  01cb  clrf    0x4b                                   ; reg: 0x04b
1949:  01ca  clrf    0x4a                                   ; reg: 0x04a
194a:  1ed0  btfss   0x50, 0x5                              ; reg: 0x050
194b:  294f  goto    label_257
194c:  3007  movlw   0x07
194d:  05dd  andwf   0x5d, F                                ; reg: 0x05d
194e:  2950  goto    label_258

label_257:                                                  ; address: 0x194f

194f:  01dd  clrf    0x5d                                   ; reg: 0x05d

label_258:                                                  ; address: 0x1950

1950:  3007  movlw   0x07
1951:  00ad  movwf   0x2d                                   ; reg: 0x02d
1952:  1fdd  btfss   0x5d, 0x7                              ; reg: 0x05d
1953:  2957  goto    label_259
1954:  1edd  btfss   0x5d, 0x5                              ; reg: 0x05d
1955:  2957  goto    label_259
1956:  29d0  goto    label_283

label_259:                                                  ; address: 0x1957

1957:  1ed6  btfss   0x56, 0x5                              ; reg: 0x056
1958:  2967  goto    label_264
1959:  084b  movf    0x4b, W                                ; reg: 0x04b
195a:  3c00  sublw   0x00

label_260:                                                  ; address: 0x195b

195b:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
195c:  2967  goto    label_264
195d:  3aff  xorlw   0xff
195e:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
195f:  2964  goto    label_262

label_261:                                                  ; address: 0x1960

1960:  084a  movf    0x4a, W                                ; reg: 0x04a
1961:  3c68  sublw   0x68
1962:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1963:  2967  goto    label_264

label_262:                                                  ; address: 0x1964

1964:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a

label_263:                                                  ; address: 0x1965

1965:  27d3  call    function_048
1966:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a

label_264:                                                  ; address: 0x1967

1967:  3001  movlw   0x01
1968:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1969:  00c8  movwf   0x48                                   ; reg: 0x048
196a:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
196b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
196c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
196d:  25b1  call    function_023

label_265:                                                  ; address: 0x196e

196e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
196f:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1970:  0857  movf    0x57, W                                ; reg: 0x057

label_266:                                                  ; address: 0x1971

1971:  3c13  sublw   0x13
1972:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1973:  2976  goto    label_267
1974:  01cb  clrf    0x4b                                   ; reg: 0x04b
1975:  01ca  clrf    0x4a                                   ; reg: 0x04a

label_267:                                                  ; address: 0x1976

1976:  084b  movf    0x4b, W                                ; reg: 0x04b
1977:  3c15  sublw   0x15
1978:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1979:  2981  goto    label_270
197a:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
197b:  2980  goto    label_269
197c:  084a  movf    0x4a, W                                ; reg: 0x04a

label_268:                                                  ; address: 0x197d

197d:  3c17  sublw   0x17
197e:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
197f:  2981  goto    label_270

label_269:                                                  ; address: 0x1980

1980:  2e5d  goto    label_371

label_270:                                                  ; address: 0x1981

1981:  0857  movf    0x57, W                                ; reg: 0x057
1982:  3c13  sublw   0x13

label_271:                                                  ; address: 0x1983

1983:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1984:  2986  goto    label_272
1985:  2e5d  goto    label_371

label_272:                                                  ; address: 0x1986

1986:  1ed6  btfss   0x56, 0x5                              ; reg: 0x056
1987:  2989  goto    label_273
1988:  2e5d  goto    label_371

label_273:                                                  ; address: 0x1989

1989:  1ed0  btfss   0x50, 0x5                              ; reg: 0x050
198a:  298f  goto    label_274
198b:  3007  movlw   0x07
198c:  05cc  andwf   0x4c, F                                ; reg: 0x04c
198d:  16cc  bsf     0x4c, 0x5                              ; reg: 0x04c
198e:  2991  goto    label_275

label_274:                                                  ; address: 0x198f

198f:  3020  movlw   0x20
1990:  00cc  movwf   0x4c                                   ; reg: 0x04c

label_275:                                                  ; address: 0x1991

1991:  19b0  btfsc   0x30, 0x3                              ; reg: 0x030
1992:  299b  goto    label_276
1993:  1b30  btfsc   0x30, 0x6                              ; reg: 0x030
1994:  299b  goto    label_276
1995:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1996:  2400  call    function_052
1997:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1998:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1999:  2400  call    0x0400
199a:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_276:                                                  ; address: 0x199b

199b:  19d1  btfsc   0x51, 0x3                              ; reg: 0x051
199c:  29a0  goto    0x01a0
199d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
199e:  27d3  call    function_048
199f:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
19a0:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a

label_277:                                                  ; address: 0x19a1

19a1:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
19a2:  21d5  call    function_007
19a3:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
19a4:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
19a5:  01cb  clrf    0x4b                                   ; reg: 0x04b
19a6:  01ca  clrf    0x4a                                   ; reg: 0x04a
19a7:  19cc  btfsc   0x4c, 0x3                              ; reg: 0x04c
19a8:  29b8  goto    label_280

label_278:                                                  ; address: 0x19a9

19a9:  1ed0  btfss   0x50, 0x5                              ; reg: 0x050
19aa:  29b8  goto    label_280
19ab:  306a  movlw   0x6a
19ac:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
19ad:  00da  movwf   0x5a                                   ; reg: 0x05a
19ae:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
19af:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
19b0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
19b1:  23d0  call    function_017
19b2:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
19b3:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
19b4:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
19b5:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
19b6:  29b8  goto    label_280

label_279:                                                  ; address: 0x19b7

19b7:  29d0  goto    label_283

label_280:                                                  ; address: 0x19b8

19b8:  1add  btfsc   0x5d, 0x5                              ; reg: 0x05d
19b9:  29cd  goto    label_282
19ba:  11dd  bcf     0x5d, 0x3                              ; reg: 0x05d
19bb:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
19bc:  01c9  clrf    0x49                                   ; reg: 0x049
19bd:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
19be:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
19bf:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
19c0:  257c  call    function_022
19c1:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
19c2:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_281:                                                  ; address: 0x19c3

19c3:  302a  movlw   0x2a
19c4:  00cb  movwf   0x4b                                   ; reg: 0x04b
19c5:  3030  movlw   0x30
19c6:  00ca  movwf   0x4a                                   ; reg: 0x04a
19c7:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
19c8:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
19c9:  228d  call    function_012
19ca:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
19cb:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
19cc:  2e5d  goto    label_371

label_282:                                                  ; address: 0x19cd

19cd:  1fdd  btfss   0x5d, 0x7                              ; reg: 0x05d
19ce:  2e5d  goto    label_371
19cf:  1330  bcf     0x30, 0x6                              ; reg: 0x030

label_283:                                                  ; address: 0x19d0

19d0:  1250  bcf     0x50, 0x4                              ; reg: 0x050
19d1:  127e  bcf     (Common_RAM + 14), 0x4                 ; reg: 0x07e
19d2:  12fe  bcf     (Common_RAM + 14), 0x5                 ; reg: 0x07e
19d3:  30dc  movlw   0xdc
19d4:  00da  movwf   0x5a                                   ; reg: 0x05a
19d5:  01df  clrf    0x5f                                   ; reg: 0x05f
19d6:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
19d7:  01c2  clrf    0x42                                   ; reg: 0x042

label_284:                                                  ; address: 0x19d8

19d8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
19d9:  11d1  bcf     0x51, 0x3                              ; reg: 0x051
19da:  01cd  clrf    0x4d                                   ; reg: 0x04d
19db:  01b0  clrf    0x30                                   ; reg: 0x030

function_063:                                               ; address: 0x19dc

19dc:  01cc  clrf    0x4c                                   ; reg: 0x04c

label_285:                                                  ; address: 0x19dd

19dd:  3007  movlw   0x07
19de:  00ad  movwf   0x2d                                   ; reg: 0x02d

label_286:                                                  ; address: 0x19df

19df:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
19e0:  01c9  clrf    0x49                                   ; reg: 0x049
19e1:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
19e2:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
19e3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
19e4:  257c  call    function_022
19e5:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
19e6:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
19e7:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
19e8:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
19e9:  228d  call    function_012
19ea:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
19eb:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
19ec:  16c3  bsf     0x43, 0x5                              ; reg: 0x043
19ed:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
19ee:  2381  call    function_051
19ef:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
19f0:  127e  bcf     (Common_RAM + 14), 0x4                 ; reg: 0x07e
19f1:  12fe  bcf     (Common_RAM + 14), 0x5                 ; reg: 0x07e
19f2:  30dc  movlw   0xdc
19f3:  00da  movwf   0x5a                                   ; reg: 0x05a
19f4:  1edd  btfss   0x5d, 0x5                              ; reg: 0x05d
19f5:  29f7  goto    0x01f7
19f6:  15dd  bsf     0x5d, 0x3                              ; reg: 0x05d
19f7:  0acd  incf    0x4d, F                                ; reg: 0x04d
19f8:  1e50  btfss   0x50, 0x4                              ; reg: 0x050
19f9:  29fc  goto    0x01fc
19fa:  3004  movlw   0x04
19fb:  00cd  movwf   0x4d                                   ; reg: 0x04d
19fc:  3030  movlw   0x30
19fd:  04cc  iorwf   0x4c, F                                ; reg: 0x04c
19fe:  3003  movlw   0x03
19ff:  00fc  movwf   (Common_RAM + 12)                      ; reg: 0x07c
1a00:  08fc  movf    (Common_RAM + 12), F                   ; reg: 0x07c
1a01:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1a02:  2a0b  goto    0x020b
1a03:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a04:  2400  call    0x0400
1a05:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1a06:  1db0  btfss   0x30, 0x3                              ; reg: 0x030
1a07:  2a09  goto    0x0209
1a08:  0acd  incf    0x4d, F                                ; reg: 0x04d
1a09:  03fc  decf    (Common_RAM + 12), F                   ; reg: 0x07c
1a0a:  2a00  goto    0x0200
1a0b:  12dd  bcf     0x5d, 0x5                              ; reg: 0x05d
1a0c:  13dd  bcf     0x5d, 0x7                              ; reg: 0x05d
1a0d:  01cb  clrf    0x4b                                   ; reg: 0x04b
1a0e:  01ca  clrf    0x4a                                   ; reg: 0x04a
1a0f:  01fc  clrf    (Common_RAM + 12)                      ; reg: 0x07c
1a10:  01fd  clrf    (Common_RAM + 13)                      ; reg: 0x07d
1a11:  13d1  bcf     0x51, 0x7                              ; reg: 0x051
1a12:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a13:  2432  call    0x0432
1a14:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1a15:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
1a16:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1a17:  2a1c  goto    0x021c
1a18:  1b5d  btfsc   0x5d, 0x6                              ; reg: 0x05d
1a19:  2a1c  goto    0x021c
1a1a:  1db0  btfss   0x30, 0x3                              ; reg: 0x030
1a1b:  2a20  goto    0x0220
1a1c:  1b5d  btfsc   0x5d, 0x6                              ; reg: 0x05d
1a1d:  2a1f  goto    0x021f
1a1e:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
1a1f:  2922  goto    0x0122
1a20:  01cb  clrf    0x4b                                   ; reg: 0x04b
1a21:  01ca  clrf    0x4a                                   ; reg: 0x04a

label_287:                                                  ; address: 0x1a22

1a22:  301c  movlw   0x1c
1a23:  00f2  movwf   (Common_RAM + 2)                       ; reg: 0x072
1a24:  3020  movlw   0x20

label_288:                                                  ; address: 0x1a25

1a25:  00f1  movwf   (Common_RAM + 1)                       ; reg: 0x071
1a26:  1486  bsf     PORTB, RB1                             ; reg: 0x006, bit: 1
1a27:  13fe  bcf     (Common_RAM + 14), 0x7                 ; reg: 0x07e
1a28:  1fad  btfss   0x2d, 0x7                              ; reg: 0x02d

label_289:                                                  ; address: 0x1a29

1a29:  2a38  goto    0x0238
1a2a:  1a7e  btfsc   (Common_RAM + 14), 0x4                 ; reg: 0x07e
1a2b:  2a38  goto    0x0238
1a2c:  301c  movlw   0x1c
1a2d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a2e:  00d3  movwf   0x53                                   ; reg: 0x053
1a2f:  3020  movlw   0x20
1a30:  00d2  movwf   0x52                                   ; reg: 0x052
1a31:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1a32:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a33:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a34:  2624  call    function_026
1a35:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1a36:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1a37:  2a59  goto    label_290
1a38:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
1a39:  0d7d  rlf     (Common_RAM + 13), W                   ; reg: 0x07d
1a3a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a3b:  00c8  movwf   0x48                                   ; reg: 0x048
1a3c:  0a48  incf    0x48, W                                ; reg: 0x048
1a3d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1a3e:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a3f:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a40:  2060  call    function_001
1a41:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1a42:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1a43:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1a44:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a45:  0848  movf    0x48, W                                ; reg: 0x048
1a46:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1a47:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a48:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a49:  2060  call    function_001
1a4a:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1a4b:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1a4c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a4d:  00c9  movwf   0x49                                   ; reg: 0x049
1a4e:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1a4f:  00ca  movwf   0x4a                                   ; reg: 0x04a
1a50:  00ce  movwf   0x4e                                   ; reg: 0x04e
1a51:  0849  movf    0x49, W                                ; reg: 0x049
1a52:  00cd  movwf   0x4d                                   ; reg: 0x04d
1a53:  3059  movlw   0x59
1a54:  00cf  movwf   0x4f                                   ; reg: 0x04f
1a55:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a56:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a57:  2546  call    function_055
1a58:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_290:                                                  ; address: 0x1a59

1a59:  084c  movf    0x4c, W                                ; reg: 0x04c
1a5a:  39f8  andlw   0xf8

label_291:                                                  ; address: 0x1a5b

1a5b:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a5c:  00c8  movwf   0x48                                   ; reg: 0x048
1a5d:  1e7e  btfss   (Common_RAM + 14), 0x4                 ; reg: 0x07e

label_292:                                                  ; address: 0x1a5e

1a5e:  2a61  goto    0x0261
1a5f:  3001  movlw   0x01
1a60:  2a62  goto    0x0262
1a61:  3000  movlw   0x00
1a62:  0748  addwf   0x48, W                                ; reg: 0x048
1a63:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a64:  00cc  movwf   0x4c                                   ; reg: 0x04c
1a65:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a66:  2d5d  goto    0x055d

label_293:                                                  ; address: 0x1a67

1a67:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_294:                                                  ; address: 0x1a68

1a68:  1fad  btfss   0x2d, 0x7                              ; reg: 0x02d
1a69:  2a9a  goto    0x029a
1a6a:  3023  movlw   0x23
1a6b:  075a  addwf   0x5a, W                                ; reg: 0x05a
1a6c:  0257  subwf   0x57, W                                ; reg: 0x057
1a6d:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1a6e:  2a9a  goto    0x029a
1a6f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1a70:  2a9a  goto    0x029a
1a71:  1a7e  btfsc   (Common_RAM + 14), 0x4                 ; reg: 0x07e
1a72:  2a9a  goto    0x029a
1a73:  167e  bsf     (Common_RAM + 14), 0x4                 ; reg: 0x07e

label_295:                                                  ; address: 0x1a74

1a74:  1d2d  btfss   0x2d, 0x2                              ; reg: 0x02d
1a75:  2a79  goto    0x0279
1a76:  01fa  clrf    (Common_RAM + 10)                      ; reg: 0x07a
1a77:  3000  movlw   0x00

label_296:                                                  ; address: 0x1a78

1a78:  2a7c  goto    0x027c
1a79:  3002  movlw   0x02
1a7a:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1a7b:  301c  movlw   0x1c

label_297:                                                  ; address: 0x1a7c

1a7c:  3ed0  addlw   0xd0
1a7d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a7e:  00c8  movwf   0x48                                   ; reg: 0x048
1a7f:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1a80:  00c9  movwf   0x49                                   ; reg: 0x049
1a81:  3002  movlw   0x02
1a82:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1a83:  3003  movlw   0x03
1a84:  07c9  addwf   0x49, F                                ; reg: 0x049
1a85:  0849  movf    0x49, W                                ; reg: 0x049
1a86:  00d4  movwf   0x54                                   ; reg: 0x054
1a87:  0848  movf    0x48, W                                ; reg: 0x048
1a88:  00d3  movwf   0x53                                   ; reg: 0x053
1a89:  305b  movlw   0x5b
1a8a:  00d5  movwf   0x55                                   ; reg: 0x055
1a8b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1a8c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1a8d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1a8e:  2422  call    function_019
1a8f:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a

label_298:                                                  ; address: 0x1a90

1a90:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1a91:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1a92:  074a  addwf   0x4a, W                                ; reg: 0x04a
1a93:  00db  movwf   0x5b                                   ; reg: 0x05b
1a94:  084b  movf    0x4b, W                                ; reg: 0x04b
1a95:  00dc  movwf   0x5c                                   ; reg: 0x05c
1a96:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1a97:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1a98:  0f79  incfsz  (Common_RAM + 9), W                    ; reg: 0x079
1a99:  07dc  addwf   0x5c, F                                ; reg: 0x05c
1a9a:  1a7e  btfsc   (Common_RAM + 14), 0x4                 ; reg: 0x07e
1a9b:  2aa9  goto    label_302
1a9c:  3004  movlw   0x04
1a9d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_299:                                                  ; address: 0x1a9e

1a9e:  00c9  movwf   0x49                                   ; reg: 0x049
1a9f:  305c  movlw   0x5c
1aa0:  00c8  movwf   0x48                                   ; reg: 0x048
1aa1:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a

label_300:                                                  ; address: 0x1aa2

1aa2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1aa3:  25a1  call    function_056
1aa4:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1aa5:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079

label_301:                                                  ; address: 0x1aa6

1aa6:  00dc  movwf   0x5c                                   ; reg: 0x05c
1aa7:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1aa8:  00db  movwf   0x5b                                   ; reg: 0x05b

label_302:                                                  ; address: 0x1aa9

1aa9:  085c  movf    0x5c, W                                ; reg: 0x05c

label_303:                                                  ; address: 0x1aaa

1aaa:  024b  subwf   0x4b, W                                ; reg: 0x04b
1aab:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1aac:  2add  goto    0x02dd
1aad:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2

label_304:                                                  ; address: 0x1aae

1aae:  2ab3  goto    0x02b3
1aaf:  085b  movf    0x5b, W                                ; reg: 0x05b
1ab0:  024a  subwf   0x4a, W                                ; reg: 0x04a
1ab1:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0

label_305:                                                  ; address: 0x1ab2

1ab2:  2add  goto    0x02dd
1ab3:  1fad  btfss   0x2d, 0x7                              ; reg: 0x02d
1ab4:  2abb  goto    0x02bb

label_306:                                                  ; address: 0x1ab5

1ab5:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1ab6:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1ab7:  228d  call    function_012
1ab8:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1ab9:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1aba:  12fe  bcf     (Common_RAM + 14), 0x5                 ; reg: 0x07e
1abb:  305a  movlw   0x5a
1abc:  075b  addwf   0x5b, W                                ; reg: 0x05b
1abd:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1abe:  085c  movf    0x5c, W                                ; reg: 0x05c
1abf:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1ac0:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1ac1:  0afa  incf    (Common_RAM + 10), F                   ; reg: 0x07a
1ac2:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1ac3:  024b  subwf   0x4b, W                                ; reg: 0x04b
1ac4:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1ac5:  2adc  goto    label_309
1ac6:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1ac7:  2acc  goto    label_307
1ac8:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1ac9:  024a  subwf   0x4a, W                                ; reg: 0x04a
1aca:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1acb:  2adc  goto    label_309

label_307:                                                  ; address: 0x1acc

1acc:  1ed6  btfss   0x56, 0x5                              ; reg: 0x056
1acd:  2ad4  goto    label_308
1ace:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1acf:  27d3  call    function_048
1ad0:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1ad1:  12dd  bcf     0x5d, 0x5                              ; reg: 0x05d
1ad2:  13dd  bcf     0x5d, 0x7                              ; reg: 0x05d
1ad3:  2adc  goto    0x02dc

label_308:                                                  ; address: 0x1ad4

1ad4:  1fdd  btfss   0x5d, 0x7                              ; reg: 0x05d
1ad5:  2adc  goto    0x02dc
1ad6:  1edd  btfss   0x5d, 0x5                              ; reg: 0x05d
1ad7:  2adc  goto    0x02dc
1ad8:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1ad9:  2000  call    function_050
1ada:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1adb:  2e5d  goto    0x065d

label_309:                                                  ; address: 0x1adc

1adc:  2b1e  goto    0x031e
1add:  084b  movf    0x4b, W                                ; reg: 0x04b
1ade:  3c03  sublw   0x03
1adf:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1ae0:  2b1e  goto    0x031e
1ae1:  3aff  xorlw   0xff
1ae2:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1ae3:  2ae8  goto    0x02e8
1ae4:  084a  movf    0x4a, W                                ; reg: 0x04a
1ae5:  3c37  sublw   0x37
1ae6:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1ae7:  2b1e  goto    0x031e
1ae8:  084b  movf    0x4b, W                                ; reg: 0x04b
1ae9:  3c04  sublw   0x04
1aea:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1aeb:  2b1e  goto    0x031e
1aec:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1aed:  2af2  goto    0x02f2
1aee:  084a  movf    0x4a, W                                ; reg: 0x04a
1aef:  3c97  sublw   0x97
1af0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1af1:  2b1e  goto    0x031e
1af2:  1ad6  btfsc   0x56, 0x5                              ; reg: 0x056
1af3:  2af9  goto    0x02f9
1af4:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1af5:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1af6:  226a  call    function_010
1af7:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1af8:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1af9:  084b  movf    0x4b, W                                ; reg: 0x04b
1afa:  3c03  sublw   0x03
1afb:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1afc:  2b1e  goto    label_314
1afd:  3aff  xorlw   0xff
1afe:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1aff:  2b04  goto    label_310
1b00:  084a  movf    0x4a, W                                ; reg: 0x04a
1b01:  3c5b  sublw   0x5b
1b02:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1b03:  2b1e  goto    label_314

label_310:                                                  ; address: 0x1b04

1b04:  1bad  btfsc   0x2d, 0x7                              ; reg: 0x02d
1b05:  2b1e  goto    label_314
1b06:  182d  btfsc   0x2d, 0x0                              ; reg: 0x02d
1b07:  2b0a  goto    label_311
1b08:  1cad  btfss   0x2d, 0x1                              ; reg: 0x02d
1b09:  2b1e  goto    label_314

label_311:                                                  ; address: 0x1b0a

1b0a:  1afe  btfsc   (Common_RAM + 14), 0x5                 ; reg: 0x07e
1b0b:  2b1e  goto    label_314
1b0c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b0d:  2df4  goto    label_224

label_312:                                                  ; address: 0x1b0e

1b0e:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1b0f:  0857  movf    0x57, W                                ; reg: 0x057
1b10:  00da  movwf   0x5a                                   ; reg: 0x05a
1b11:  085a  movf    0x5a, W                                ; reg: 0x05a
1b12:  3c96  sublw   0x96
1b13:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1b14:  2b17  goto    label_313
1b15:  3096  movlw   0x96
1b16:  00da  movwf   0x5a                                   ; reg: 0x05a

label_313:                                                  ; address: 0x1b17

1b17:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b18:  0822  movf    0x22, W                                ; reg: 0x022
1b19:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b1a:  00d9  movwf   0x59                                   ; reg: 0x059
1b1b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b1c:  25fd  call    function_057
1b1d:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_314:                                                  ; address: 0x1b1e

1b1e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b1f:  01c9  clrf    0x49                                   ; reg: 0x049
1b20:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1b21:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b22:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b23:  257c  call    function_022
1b24:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1b25:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1b26:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b27:  2432  call    function_053
1b28:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1b29:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
1b2a:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1b2b:  2b2d  goto    0x032d
1b2c:  2922  goto    0x0122
1b2d:  087d  movf    (Common_RAM + 13), W                   ; reg: 0x07d
1b2e:  3c02  sublw   0x02
1b2f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1b30:  2b58  goto    0x0358
1b31:  3001  movlw   0x01
1b32:  077d  addwf   (Common_RAM + 13), W                   ; reg: 0x07d
1b33:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
1b34:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
1b35:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
1b36:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
1b37:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b38:  00c9  movwf   0x49                                   ; reg: 0x049
1b39:  0a49  incf    0x49, W                                ; reg: 0x049
1b3a:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1b3b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b3c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b3d:  2054  call    function_000
1b3e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1b3f:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1b40:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1b41:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b42:  0849  movf    0x49, W                                ; reg: 0x049
1b43:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1b44:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b45:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b46:  2054  call    function_000
1b47:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1b48:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1b49:  00f8  movwf   (Common_RAM + 8)                       ; reg: 0x078
1b4a:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1b4b:  024b  subwf   0x4b, W                                ; reg: 0x04b
1b4c:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1b4d:  2b58  goto    label_316
1b4e:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1b4f:  2b54  goto    label_315
1b50:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1b51:  024a  subwf   0x4a, W                                ; reg: 0x04a
1b52:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1b53:  2b58  goto    label_316

label_315:                                                  ; address: 0x1b54

1b54:  0afd  incf    (Common_RAM + 13), F                   ; reg: 0x07d
1b55:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b56:  25fd  call    function_057
1b57:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_316:                                                  ; address: 0x1b58

1b58:  3007  movlw   0x07
1b59:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b5a:  00c9  movwf   0x49                                   ; reg: 0x049
1b5b:  3008  movlw   0x08
1b5c:  00c8  movwf   0x48                                   ; reg: 0x048
1b5d:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1b5e:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b5f:  25a1  call    0x05a1
1b60:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1b61:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1b62:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1b63:  084b  movf    0x4b, W                                ; reg: 0x04b
1b64:  027a  subwf   (Common_RAM + 10), W                   ; reg: 0x07a
1b65:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1b66:  2b6f  goto    0x036f
1b67:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1b68:  2b6d  goto    0x036d
1b69:  084a  movf    0x4a, W                                ; reg: 0x04a
1b6a:  0278  subwf   (Common_RAM + 8), W                    ; reg: 0x078
1b6b:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1b6c:  2b6f  goto    0x036f
1b6d:  01e0  clrf    0x60                                   ; reg: 0x060
1b6e:  2e5d  goto    0x065d
1b6f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b70:  1ba2  btfsc   0x22, 0x7                              ; reg: 0x022
1b71:  2b79  goto    0x0379
1b72:  0822  movf    0x22, W                                ; reg: 0x022
1b73:  3c00  sublw   0x00
1b74:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1b75:  2b79  goto    0x0379
1b76:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
1b77:  0c22  rrf     0x22, W                                ; reg: 0x022
1b78:  2b7a  goto    0x037a
1b79:  3000  movlw   0x00
1b7a:  3e3c  addlw   0x3c
1b7b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b7c:  0257  subwf   0x57, W                                ; reg: 0x057
1b7d:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1b7e:  2b81  goto    0x0381
1b7f:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1b80:  2b9e  goto    0x039e
1b81:  0860  movf    0x60, W                                ; reg: 0x060
1b82:  3c04  sublw   0x04
1b83:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1b84:  2b9d  goto    0x039d
1b85:  306e  movlw   0x6e
1b86:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b87:  00da  movwf   0x5a                                   ; reg: 0x05a
1b88:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a

label_317:                                                  ; address: 0x1b89

1b89:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a

label_318:                                                  ; address: 0x1b8a

1b8a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1b8b:  23d0  call    function_017
1b8c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1b8d:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1b8e:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
1b8f:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1b90:  2b93  goto    label_319
1b91:  3000  movlw   0x00
1b92:  2b94  goto    label_320

label_319:                                                  ; address: 0x1b93

1b93:  3001  movlw   0x01

label_320:                                                  ; address: 0x1b94

1b94:  3902  andlw   0x02
1b95:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1b96:  2b9c  goto    label_321
1b97:  084d  movf    0x4d, W                                ; reg: 0x04d
1b98:  3c01  sublw   0x01
1b99:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1b9a:  2b9c  goto    label_321
1b9b:  29dd  goto    label_285

label_321:                                                  ; address: 0x1b9c

1b9c:  2921  goto    label_252
1b9d:  2bad  goto    label_323
1b9e:  0857  movf    0x57, W                                ; reg: 0x057
1b9f:  3cfd  sublw   0xfd
1ba0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1ba1:  2ba4  goto    label_322
1ba2:  01e0  clrf    0x60                                   ; reg: 0x060
1ba3:  2bad  goto    label_323

label_322:                                                  ; address: 0x1ba4

1ba4:  0860  movf    0x60, W                                ; reg: 0x060
1ba5:  3c38  sublw   0x38
1ba6:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1ba7:  2bad  goto    label_323
1ba8:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
1ba9:  1530  bsf     0x30, 0x2                              ; reg: 0x030
1baa:  30b4  movlw   0xb4
1bab:  00df  movwf   0x5f                                   ; reg: 0x05f
1bac:  2922  goto    label_253

label_323:                                                  ; address: 0x1bad

1bad:  300b  movlw   0x0b
1bae:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1baf:  00c9  movwf   0x49                                   ; reg: 0x049
1bb0:  3040  movlw   0x40
1bb1:  00c8  movwf   0x48                                   ; reg: 0x048
1bb2:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1bb3:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1bb4:  25a1  call    function_056
1bb5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1bb6:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1bb7:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1bb8:  084b  movf    0x4b, W                                ; reg: 0x04b
1bb9:  027a  subwf   (Common_RAM + 10), W                   ; reg: 0x07a
1bba:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1bbb:  2bc3  goto    0x03c3
1bbc:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1bbd:  2bc2  goto    0x03c2
1bbe:  084a  movf    0x4a, W                                ; reg: 0x04a
1bbf:  0278  subwf   (Common_RAM + 8), W                    ; reg: 0x078
1bc0:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1bc1:  2bc3  goto    0x03c3
1bc2:  2e5d  goto    0x065d
1bc3:  3001  movlw   0x01
1bc4:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1bc5:  00c9  movwf   0x49                                   ; reg: 0x049
1bc6:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1bc7:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1bc8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1bc9:  257c  call    function_022
1bca:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1bcb:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1bcc:  300c  movlw   0x0c
1bcd:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1bce:  00c9  movwf   0x49                                   ; reg: 0x049
1bcf:  30a8  movlw   0xa8
1bd0:  00c8  movwf   0x48                                   ; reg: 0x048

label_324:                                                  ; address: 0x1bd1

1bd1:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a

label_325:                                                  ; address: 0x1bd2

1bd2:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1bd3:  25a1  call    function_056
1bd4:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1bd5:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1bd6:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1bd7:  084b  movf    0x4b, W                                ; reg: 0x04b
1bd8:  027a  subwf   (Common_RAM + 10), W                   ; reg: 0x07a
1bd9:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0

label_326:                                                  ; address: 0x1bda

1bda:  2be2  goto    0x03e2
1bdb:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1bdc:  2be1  goto    0x03e1
1bdd:  084a  movf    0x4a, W                                ; reg: 0x04a
1bde:  0278  subwf   (Common_RAM + 8), W                    ; reg: 0x078
1bdf:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1be0:  2be2  goto    0x03e2
1be1:  2e5d  goto    0x065d
1be2:  01cb  clrf    0x4b                                   ; reg: 0x04b
1be3:  01ca  clrf    0x4a                                   ; reg: 0x04a
1be4:  1ed0  btfss   0x50, 0x5                              ; reg: 0x050
1be5:  2bed  goto    0x03ed
1be6:  085d  movf    0x5d, W                                ; reg: 0x05d

function_064:                                               ; address: 0x1be7

1be7:  3907  andlw   0x07
1be8:  05cc  andwf   0x4c, F                                ; reg: 0x04c
1be9:  3050  movlw   0x50
1bea:  04cc  iorwf   0x4c, F                                ; reg: 0x04c
1beb:  12d0  bcf     0x50, 0x5                              ; reg: 0x050
1bec:  2bef  goto    0x03ef
1bed:  3053  movlw   0x53
1bee:  00cc  movwf   0x4c                                   ; reg: 0x04c
1bef:  127e  bcf     (Common_RAM + 14), 0x4                 ; reg: 0x07e
1bf0:  01f5  clrf    (Common_RAM + 5)                       ; reg: 0x075
1bf1:  0875  movf    (Common_RAM + 5), W                    ; reg: 0x075
1bf2:  3c07  sublw   0x07
1bf3:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1bf4:  2bfc  goto    0x03fc
1bf5:  3063  movlw   0x63
1bf6:  0775  addwf   (Common_RAM + 5), W                    ; reg: 0x075
1bf7:  0084  movwf   FSR                                    ; reg: 0x004
1bf8:  0857  movf    0x57, W                                ; reg: 0x057
1bf9:  0080  movwf   INDF                                   ; reg: 0x000
1bfa:  0af5  incf    (Common_RAM + 5), F                    ; reg: 0x075
1bfb:  2bf1  goto    0x03f1
1bfc:  30ff  movlw   0xff
1bfd:  00da  movwf   0x5a                                   ; reg: 0x05a
1bfe:  01ec  clrf    0x6c                                   ; reg: 0x06c
1bff:  2e5d  goto    0x065d
1c00:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c01:  01c9  clrf    0x49                                   ; reg: 0x049
1c02:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1c03:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c04:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c05:  257c  call    function_022
1c06:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1c07:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c08:  084c  movf    0x4c, W                                ; reg: 0x04c
1c09:  3907  andlw   0x07
1c0a:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
1c0b:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
1c0c:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
1c0d:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
1c0e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c0f:  00c9  movwf   0x49                                   ; reg: 0x049
1c10:  0a49  incf    0x49, W                                ; reg: 0x049
1c11:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1c12:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c13:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c14:  207a  call    function_002
1c15:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1c16:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c17:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1c18:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c19:  0849  movf    0x49, W                                ; reg: 0x049
1c1a:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1c1b:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c1c:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c1d:  207a  call    function_002
1c1e:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1c1f:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c20:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c21:  00ca  movwf   0x4a                                   ; reg: 0x04a
1c22:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1c23:  00cb  movwf   0x4b                                   ; reg: 0x04b
1c24:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c25:  084c  movf    0x4c, W                                ; reg: 0x04c
1c26:  3907  andlw   0x07
1c27:  3e48  addlw   0x48
1c28:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c29:  00cc  movwf   0x4c                                   ; reg: 0x04c
1c2a:  084b  movf    0x4b, W                                ; reg: 0x04b
1c2b:  00ce  movwf   0x4e                                   ; reg: 0x04e
1c2c:  084a  movf    0x4a, W                                ; reg: 0x04a
1c2d:  00cd  movwf   0x4d                                   ; reg: 0x04d
1c2e:  084c  movf    0x4c, W                                ; reg: 0x04c
1c2f:  00cf  movwf   0x4f                                   ; reg: 0x04f
1c30:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c31:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c32:  2546  call    function_055
1c33:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c34:  1fdd  btfss   0x5d, 0x7                              ; reg: 0x05d
1c35:  2c3c  goto    0x043c
1c36:  1edd  btfss   0x5d, 0x5                              ; reg: 0x05d
1c37:  2c3c  goto    0x043c
1c38:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c39:  2000  call    0x0000
1c3a:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c3b:  2e5d  goto    0x065d
1c3c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c3d:  2432  call    0x0432
1c3e:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c3f:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
1c40:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1c41:  2c43  goto    0x0443
1c42:  2922  goto    0x0122
1c43:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c44:  2e4b  goto    0x064b

label_327:                                                  ; address: 0x1c45

1c45:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c46:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
1c47:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1c48:  2c71  goto    0x0471
1c49:  1bfe  btfsc   (Common_RAM + 14), 0x7                 ; reg: 0x07e
1c4a:  2c4f  goto    0x044f
1c4b:  086e  movf    0x6e, W                                ; reg: 0x06e
1c4c:  3c0f  sublw   0x0f
1c4d:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1c4e:  2c54  goto    0x0454
1c4f:  14cf  bsf     0x4f, 0x1                              ; reg: 0x04f
1c50:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
1c51:  177e  bsf     (Common_RAM + 14), 0x6                 ; reg: 0x07e
1c52:  1330  bcf     0x30, 0x6                              ; reg: 0x030
1c53:  28f2  goto    0x00f2
1c54:  0860  movf    0x60, W                                ; reg: 0x060
1c55:  3c04  sublw   0x04
1c56:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1c57:  2c70  goto    0x0470
1c58:  084d  movf    0x4d, W                                ; reg: 0x04d
1c59:  3c01  sublw   0x01
1c5a:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1c5b:  2c6f  goto    0x046f
1c5c:  306e  movlw   0x6e
1c5d:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c5e:  00da  movwf   0x5a                                   ; reg: 0x05a
1c5f:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1c60:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c61:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c62:  23d0  call    function_017
1c63:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1c64:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c65:  08f8  movf    (Common_RAM + 8), F                    ; reg: 0x078
1c66:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1c67:  2c6a  goto    label_328
1c68:  3000  movlw   0x00
1c69:  2c6b  goto    label_329

label_328:                                                  ; address: 0x1c6a

1c6a:  3001  movlw   0x01

label_329:                                                  ; address: 0x1c6b

1c6b:  3902  andlw   0x02
1c6c:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1c6d:  2c6f  goto    label_330
1c6e:  29dd  goto    label_285

label_330:                                                  ; address: 0x1c6f

1c6f:  2921  goto    label_252
1c70:  2c7f  goto    label_332
1c71:  0857  movf    0x57, W                                ; reg: 0x057
1c72:  3cfd  sublw   0xfd
1c73:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1c74:  2c77  goto    label_331
1c75:  01e0  clrf    0x60                                   ; reg: 0x060
1c76:  2c7f  goto    label_332

label_331:                                                  ; address: 0x1c77

1c77:  0860  movf    0x60, W                                ; reg: 0x060
1c78:  3c38  sublw   0x38
1c79:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1c7a:  2c7f  goto    label_332
1c7b:  154f  bsf     0x4f, 0x2                              ; reg: 0x04f
1c7c:  164f  bsf     0x4f, 0x4                              ; reg: 0x04f
1c7d:  1430  bsf     0x30, 0x0                              ; reg: 0x030
1c7e:  2922  goto    label_253

label_332:                                                  ; address: 0x1c7f

1c7f:  084c  movf    0x4c, W                                ; reg: 0x04c
1c80:  3907  andlw   0x07
1c81:  00f5  movwf   (Common_RAM + 5)                       ; reg: 0x075
1c82:  085d  movf    0x5d, W                                ; reg: 0x05d
1c83:  3907  andlw   0x07
1c84:  00f6  movwf   (Common_RAM + 6)                       ; reg: 0x076
1c85:  1cd0  btfss   0x50, 0x1                              ; reg: 0x050
1c86:  2c99  goto    label_333
1c87:  3017  movlw   0x17
1c88:  00ad  movwf   0x2d                                   ; reg: 0x02d
1c89:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c8a:  2684  call    function_058
1c8b:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c8c:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1c8d:  0275  subwf   (Common_RAM + 5), W                    ; reg: 0x075
1c8e:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1c8f:  2c93  goto    0x0493
1c90:  1a4c  btfsc   0x4c, 0x4                              ; reg: 0x04c
1c91:  2c93  goto    0x0493
1c92:  2d0a  goto    0x050a
1c93:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1c94:  2684  call    0x0684
1c95:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1c96:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1c97:  00f6  movwf   (Common_RAM + 6)                       ; reg: 0x076
1c98:  2cb4  goto    0x04b4

label_333:                                                  ; address: 0x1c99

1c99:  1dcc  btfss   0x4c, 0x3                              ; reg: 0x04c
1c9a:  2cb4  goto    0x04b4
1c9b:  306a  movlw   0x6a
1c9c:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1c9d:  00da  movwf   0x5a                                   ; reg: 0x05a
1c9e:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1c9f:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1ca0:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1ca1:  23d0  call    function_017
1ca2:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1ca3:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1ca4:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1ca5:  00f6  movwf   (Common_RAM + 6)                       ; reg: 0x076
1ca6:  08f6  movf    (Common_RAM + 6), F                    ; reg: 0x076
1ca7:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1ca8:  2caf  goto    label_335
1ca9:  08f5  movf    (Common_RAM + 5), F                    ; reg: 0x075
1caa:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1cab:  2cae  goto    label_334
1cac:  16d0  bsf     0x50, 0x5                              ; reg: 0x050
1cad:  2922  goto    label_253

label_334:                                                  ; address: 0x1cae

1cae:  2cb0  goto    label_336

label_335:                                                  ; address: 0x1caf

1caf:  03f6  decf    (Common_RAM + 6), F                    ; reg: 0x076

label_336:                                                  ; address: 0x1cb0

1cb0:  0876  movf    (Common_RAM + 6), W                    ; reg: 0x076
1cb1:  0275  subwf   (Common_RAM + 5), W                    ; reg: 0x075
1cb2:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1cb3:  2cb4  goto    label_337

label_337:                                                  ; address: 0x1cb4

1cb4:  1ffe  btfss   (Common_RAM + 14), 0x7                 ; reg: 0x07e
1cb5:  2cb7  goto    label_338
1cb6:  2e5d  goto    label_371

label_338:                                                  ; address: 0x1cb7

1cb7:  1e4c  btfss   0x4c, 0x4                              ; reg: 0x04c
1cb8:  2ce6  goto    label_344
1cb9:  08ec  movf    0x6c, F                                ; reg: 0x06c
1cba:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1cbb:  2ccb  goto    label_340
1cbc:  0857  movf    0x57, W                                ; reg: 0x057
1cbd:  00ec  movwf   0x6c                                   ; reg: 0x06c
1cbe:  300b  movlw   0x0b
1cbf:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1cc0:  00d3  movwf   0x53                                   ; reg: 0x053
1cc1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1cc2:  086c  movf    0x6c, W                                ; reg: 0x06c
1cc3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1cc4:  00d4  movwf   0x54                                   ; reg: 0x054
1cc5:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1cc6:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1cc7:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1cc8:  22bc  call    function_014

label_339:                                                  ; address: 0x1cc9

1cc9:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1cca:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_340:                                                  ; address: 0x1ccb

1ccb:  0876  movf    (Common_RAM + 6), W                    ; reg: 0x076
1ccc:  0275  subwf   (Common_RAM + 5), W                    ; reg: 0x075
1ccd:  1903  btfsc   STATUS, Z                              ; reg: 0x003, bit: 2
1cce:  2ce4  goto    label_343
1ccf:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a

label_341:                                                  ; address: 0x1cd0

1cd0:  26ab  call    function_059
1cd1:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1cd2:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1cd3:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1cd4:  084b  movf    0x4b, W                                ; reg: 0x04b
1cd5:  027a  subwf   (Common_RAM + 10), W                   ; reg: 0x07a
1cd6:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1cd7:  2ce0  goto    0x04e0
1cd8:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1cd9:  2cde  goto    0x04de

label_342:                                                  ; address: 0x1cda

1cda:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1cdb:  024a  subwf   0x4a, W                                ; reg: 0x04a
1cdc:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1cdd:  2ce0  goto    0x04e0
1cde:  2e5d  goto    0x065d
1cdf:  2ce3  goto    0x04e3
1ce0:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1ce1:  2718  call    0x0718
1ce2:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1ce3:  2ce5  goto    0x04e5

label_343:                                                  ; address: 0x1ce4

1ce4:  2cee  goto    0x04ee
1ce5:  2cec  goto    0x04ec

label_344:                                                  ; address: 0x1ce6

1ce6:  0876  movf    (Common_RAM + 6), W                    ; reg: 0x076
1ce7:  0275  subwf   (Common_RAM + 5), W                    ; reg: 0x075
1ce8:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1ce9:  2ceb  goto    0x04eb
1cea:  2e5d  goto    0x065d
1ceb:  2cee  goto    0x04ee
1cec:  01cb  clrf    0x4b                                   ; reg: 0x04b
1ced:  01ca  clrf    0x4a                                   ; reg: 0x04a
1cee:  164c  bsf     0x4c, 0x4                              ; reg: 0x04c
1cef:  0876  movf    (Common_RAM + 6), W                    ; reg: 0x076
1cf0:  0275  subwf   (Common_RAM + 5), W                    ; reg: 0x075
1cf1:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1cf2:  2d07  goto    0x0507
1cf3:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1cf4:  26ab  call    0x06ab
1cf5:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1cf6:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1cf7:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1cf8:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1cf9:  024b  subwf   0x4b, W                                ; reg: 0x04b
1cfa:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1cfb:  2d07  goto    0x0507
1cfc:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1cfd:  2d02  goto    0x0502
1cfe:  084a  movf    0x4a, W                                ; reg: 0x04a
1cff:  0278  subwf   (Common_RAM + 8), W                    ; reg: 0x078
1d00:  1803  btfsc   STATUS, C                              ; reg: 0x003, bit: 0
1d01:  2d07  goto    0x0507
1d02:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d03:  2718  call    0x0718
1d04:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d05:  124c  bcf     0x4c, 0x4                              ; reg: 0x04c
1d06:  01ec  clrf    0x6c                                   ; reg: 0x06c
1d07:  125d  bcf     0x5d, 0x4                              ; reg: 0x05d
1d08:  13dd  bcf     0x5d, 0x7                              ; reg: 0x05d
1d09:  2e5d  goto    0x065d
1d0a:  01cb  clrf    0x4b                                   ; reg: 0x04b
1d0b:  01ca  clrf    0x4a                                   ; reg: 0x04a
1d0c:  01fc  clrf    (Common_RAM + 12)                      ; reg: 0x07c
1d0d:  01fd  clrf    (Common_RAM + 13)                      ; reg: 0x07d
1d0e:  13d1  bcf     0x51, 0x7                              ; reg: 0x051
1d0f:  167e  bsf     (Common_RAM + 14), 0x4                 ; reg: 0x07e
1d10:  308f  movlw   0x8f
1d11:  05cc  andwf   0x4c, F                                ; reg: 0x04c
1d12:  3060  movlw   0x60
1d13:  04cc  iorwf   0x4c, F                                ; reg: 0x04c
1d14:  1251  bcf     0x51, 0x4                              ; reg: 0x051
1d15:  130b  bcf     INTCON, PEIE                           ; reg: 0x00b, bit: 6
1d16:  138b  bcf     INTCON, GIE                            ; reg: 0x00b, bit: 7
1d17:  1b8b  btfsc   INTCON, GIE                            ; reg: 0x00b, bit: 7
1d18:  2d16  goto    0x0516
1d19:  01f2  clrf    (Common_RAM + 2)                       ; reg: 0x072
1d1a:  01f1  clrf    (Common_RAM + 1)                       ; reg: 0x071
1d1b:  30c0  movlw   0xc0
1d1c:  048b  iorwf   INTCON, F                              ; reg: 0x00b
1d1d:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
1d1e:  0d7d  rlf     (Common_RAM + 13), W                   ; reg: 0x07d
1d1f:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d20:  00c8  movwf   0x48                                   ; reg: 0x048
1d21:  0a48  incf    0x48, W                                ; reg: 0x048
1d22:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d23:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d24:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d25:  2098  call    function_004
1d26:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d27:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d28:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1d29:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d2a:  0848  movf    0x48, W                                ; reg: 0x048
1d2b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d2c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d2d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d2e:  2098  call    function_004
1d2f:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d30:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d31:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d32:  00c9  movwf   0x49                                   ; reg: 0x049
1d33:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1d34:  00ca  movwf   0x4a                                   ; reg: 0x04a
1d35:  00ce  movwf   0x4e                                   ; reg: 0x04e
1d36:  0849  movf    0x49, W                                ; reg: 0x049
1d37:  00cd  movwf   0x4d                                   ; reg: 0x04d
1d38:  3061  movlw   0x61
1d39:  00cf  movwf   0x4f                                   ; reg: 0x04f
1d3a:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d3b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d3c:  2546  call    function_055
1d3d:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d3e:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d3f:  01c9  clrf    0x49                                   ; reg: 0x049
1d40:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d41:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d42:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d43:  257c  call    function_022
1d44:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d45:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d46:  085d  movf    0x5d, W                                ; reg: 0x05d
1d47:  3907  andlw   0x07
1d48:  00f6  movwf   (Common_RAM + 6)                       ; reg: 0x076
1d49:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d4a:  2684  call    function_058
1d4b:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d4c:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1d4d:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d4e:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d4f:  20a2  call    function_005
1d50:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d51:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d52:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d53:  00c9  movwf   0x49                                   ; reg: 0x049
1d54:  01ce  clrf    0x4e                                   ; reg: 0x04e
1d55:  0849  movf    0x49, W                                ; reg: 0x049
1d56:  00cd  movwf   0x4d                                   ; reg: 0x04d
1d57:  3060  movlw   0x60
1d58:  00cf  movwf   0x4f                                   ; reg: 0x04f
1d59:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d5a:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d5b:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d5c:  2477  call    function_020
1d5d:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d5e:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d5f:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1d60:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d61:  00cb  movwf   0x4b                                   ; reg: 0x04b
1d62:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1d63:  00ca  movwf   0x4a                                   ; reg: 0x04a
1d64:  084b  movf    0x4b, W                                ; reg: 0x04b
1d65:  00cf  movwf   0x4f                                   ; reg: 0x04f
1d66:  084a  movf    0x4a, W                                ; reg: 0x04a
1d67:  00ce  movwf   0x4e                                   ; reg: 0x04e
1d68:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d69:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d6a:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d6b:  2546  call    function_021
1d6c:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d6d:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d6e:  087d  movf    (Common_RAM + 13), W                   ; reg: 0x07d
1d6f:  3c01  sublw   0x01
1d70:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1d71:  2dd2  goto    label_350
1d72:  3001  movlw   0x01
1d73:  077d  addwf   (Common_RAM + 13), W                   ; reg: 0x07d
1d74:  00f7  movwf   (Common_RAM + 7)                       ; reg: 0x077
1d75:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
1d76:  0df7  rlf     (Common_RAM + 7), F                    ; reg: 0x077
1d77:  0877  movf    (Common_RAM + 7), W                    ; reg: 0x077
1d78:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d79:  00c9  movwf   0x49                                   ; reg: 0x049
1d7a:  0a49  incf    0x49, W                                ; reg: 0x049
1d7b:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d7c:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d7d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d7e:  208e  call    function_003
1d7f:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d80:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d81:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1d82:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d83:  0849  movf    0x49, W                                ; reg: 0x049
1d84:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d85:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1d86:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d87:  208e  call    function_003
1d88:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d89:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1d8a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d8b:  00ca  movwf   0x4a                                   ; reg: 0x04a
1d8c:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1d8d:  00cb  movwf   0x4b                                   ; reg: 0x04b
1d8e:  3062  movlw   0x62
1d8f:  00d6  movwf   0x56                                   ; reg: 0x056
1d90:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1d91:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d92:  20ca  call    function_038
1d93:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1d94:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1d95:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d96:  00cc  movwf   0x4c                                   ; reg: 0x04c
1d97:  084b  movf    0x4b, W                                ; reg: 0x04b
1d98:  00ce  movwf   0x4e                                   ; reg: 0x04e
1d99:  084a  movf    0x4a, W                                ; reg: 0x04a
1d9a:  00cd  movwf   0x4d                                   ; reg: 0x04d
1d9b:  084c  movf    0x4c, W                                ; reg: 0x04c
1d9c:  00cf  movwf   0x4f                                   ; reg: 0x04f
1d9d:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1d9e:  2000  call    0x0000
1d9f:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1da0:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1da1:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1da2:  024b  subwf   0x4b, W                                ; reg: 0x04b
1da3:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1da4:  2dd2  goto    0x05d2
1da5:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1da6:  2dab  goto    0x05ab
1da7:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1da8:  024a  subwf   0x4a, W                                ; reg: 0x04a
1da9:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1daa:  2dd2  goto    0x05d2
1dab:  0afd  incf    (Common_RAM + 13), F                   ; reg: 0x07d
1dac:  087d  movf    (Common_RAM + 13), W                   ; reg: 0x07d
1dad:  3c02  sublw   0x02
1dae:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1daf:  2db1  goto    0x05b1
1db0:  127e  bcf     (Common_RAM + 14), 0x4                 ; reg: 0x07e
1db1:  1003  bcf     STATUS, C                              ; reg: 0x003, bit: 0
1db2:  0d7d  rlf     (Common_RAM + 13), W                   ; reg: 0x07d
1db3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1db4:  00c8  movwf   0x48                                   ; reg: 0x048
1db5:  0a48  incf    0x48, W                                ; reg: 0x048

label_345:                                                  ; address: 0x1db6

1db6:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1db7:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1db8:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1db9:  2098  call    function_004
1dba:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1dbb:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1dbc:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a

label_346:                                                  ; address: 0x1dbd

1dbd:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1dbe:  0848  movf    0x48, W                                ; reg: 0x048

label_347:                                                  ; address: 0x1dbf

1dbf:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1dc0:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1dc1:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1dc2:  2098  call    function_004
1dc3:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1dc4:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1dc5:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1dc6:  00c9  movwf   0x49                                   ; reg: 0x049
1dc7:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1dc8:  00ca  movwf   0x4a                                   ; reg: 0x04a
1dc9:  00ce  movwf   0x4e                                   ; reg: 0x04e
1dca:  0849  movf    0x49, W                                ; reg: 0x049
1dcb:  00cd  movwf   0x4d                                   ; reg: 0x04d
1dcc:  3061  movlw   0x61
1dcd:  00cf  movwf   0x4f                                   ; reg: 0x04f

label_348:                                                  ; address: 0x1dce

1dce:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a

label_349:                                                  ; address: 0x1dcf

1dcf:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1dd0:  2546  call    function_055
1dd1:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a

label_350:                                                  ; address: 0x1dd2

1dd2:  1888  btfsc   PORTD, RD1                             ; reg: 0x008, bit: 1
1dd3:  2dd8  goto    0x05d8
1dd4:  19cf  btfsc   0x4f, 0x3                              ; reg: 0x04f
1dd5:  2dd8  goto    0x05d8
1dd6:  1c30  btfss   0x30, 0x0                              ; reg: 0x030
1dd7:  2dda  goto    0x05da

label_351:                                                  ; address: 0x1dd8

1dd8:  1651  bsf     0x51, 0x4                              ; reg: 0x051
1dd9:  2ddb  goto    0x05db
1dda:  1251  bcf     0x51, 0x4                              ; reg: 0x051
1ddb:  3062  movlw   0x62
1ddc:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1ddd:  00d6  movwf   0x56                                   ; reg: 0x056
1dde:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1ddf:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1de0:  20ca  call    function_038
1de1:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1de2:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1de3:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1de4:  00c8  movwf   0x48                                   ; reg: 0x048
1de5:  3004  movlw   0x04
1de6:  00ce  movwf   0x4e                                   ; reg: 0x04e

label_352:                                                  ; address: 0x1de7

1de7:  30b0  movlw   0xb0

label_353:                                                  ; address: 0x1de8

1de8:  00cd  movwf   0x4d                                   ; reg: 0x04d
1de9:  0848  movf    0x48, W                                ; reg: 0x048
1dea:  00cf  movwf   0x4f                                   ; reg: 0x04f
1deb:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1dec:  2000  call    0x0000
1ded:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1dee:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1def:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1df0:  024b  subwf   0x4b, W                                ; reg: 0x04b
1df1:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1df2:  2e32  goto    0x0632
1df3:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2

label_354:                                                  ; address: 0x1df4

1df4:  2df9  goto    0x05f9
1df5:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1df6:  024a  subwf   0x4a, W                                ; reg: 0x04a
1df7:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1df8:  2e32  goto    0x0632
1df9:  1bd1  btfsc   0x51, 0x7                              ; reg: 0x051
1dfa:  2e32  goto    0x0632
1dfb:  17d1  bsf     0x51, 0x7                              ; reg: 0x051
1dfc:  3027  movlw   0x27
1dfd:  00ad  movwf   0x2d                                   ; reg: 0x02d
1dfe:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1dff:  2000  call    function_050

label_355:                                                  ; address: 0x1e00

1e00:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1e01:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1e02:  118a  bcf     PCLATH, 0x3                            ; reg: 0x00a
1e03:  2255  call    function_009
1e04:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1e05:  158a  bsf     PCLATH, 0x3                            ; reg: 0x00a
1e06:  01cb  clrf    0x4b                                   ; reg: 0x04b
1e07:  01ca  clrf    0x4a                                   ; reg: 0x04a
1e08:  3037  movlw   0x37

label_356:                                                  ; address: 0x1e09

1e09:  00ad  movwf   0x2d                                   ; reg: 0x02d
1e0a:  1cd0  btfss   0x50, 0x1                              ; reg: 0x050
1e0b:  2e10  goto    label_358

label_357:                                                  ; address: 0x1e0c

1e0c:  3047  movlw   0x47
1e0d:  00ad  movwf   0x2d                                   ; reg: 0x02d
1e0e:  10d0  bcf     0x50, 0x1                              ; reg: 0x050
1e0f:  2e2d  goto    label_363

label_358:                                                  ; address: 0x1e10

1e10:  3057  movlw   0x57
1e11:  00ad  movwf   0x2d                                   ; reg: 0x02d
1e12:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1e13:  2113  call    function_040
1e14:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a

label_359:                                                  ; address: 0x1e15

1e15:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079
1e16:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1e17:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1e18:  023a  subwf   0x3a, W                                ; reg: 0x03a
1e19:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1e1a:  2e2b  goto    0x062b
1e1b:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1e1c:  2e21  goto    0x0621
1e1d:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078

label_360:                                                  ; address: 0x1e1e

1e1e:  0239  subwf   0x39, W                                ; reg: 0x039
1e1f:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1e20:  2e2b  goto    0x062b
1e21:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1e22:  2113  call    0x0113

label_361:                                                  ; address: 0x1e23

1e23:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1e24:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1e25:  02b9  subwf   0x39, F                                ; reg: 0x039
1e26:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079

label_362:                                                  ; address: 0x1e27

1e27:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1e28:  0f79  incfsz  (Common_RAM + 9), W                    ; reg: 0x079
1e29:  02ba  subwf   0x3a, F                                ; reg: 0x03a
1e2a:  2e2d  goto    0x062d
1e2b:  01ba  clrf    0x3a                                   ; reg: 0x03a
1e2c:  01b9  clrf    0x39                                   ; reg: 0x039

label_363:                                                  ; address: 0x1e2d

1e2d:  3067  movlw   0x67
1e2e:  00ad  movwf   0x2d                                   ; reg: 0x02d
1e2f:  3077  movlw   0x77

label_364:                                                  ; address: 0x1e30

1e30:  00ad  movwf   0x2d                                   ; reg: 0x02d
1e31:  01cd  clrf    0x4d                                   ; reg: 0x04d
1e32:  3062  movlw   0x62
1e33:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5

label_365:                                                  ; address: 0x1e34

1e34:  00d6  movwf   0x56                                   ; reg: 0x056
1e35:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1e36:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1e37:  20ca  call    0x00ca

label_366:                                                  ; address: 0x1e38

1e38:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a

label_367:                                                  ; address: 0x1e39

1e39:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078
1e3a:  1683  bsf     STATUS, RP0                            ; reg: 0x003, bit: 5
1e3b:  00c8  movwf   0x48                                   ; reg: 0x048
1e3c:  3005  movlw   0x05
1e3d:  00ce  movwf   0x4e                                   ; reg: 0x04e
1e3e:  3028  movlw   0x28
1e3f:  00cd  movwf   0x4d                                   ; reg: 0x04d
1e40:  0848  movf    0x48, W                                ; reg: 0x048

label_368:                                                  ; address: 0x1e41

1e41:  00cf  movwf   0x4f                                   ; reg: 0x04f
1e42:  1283  bcf     STATUS, RP0                            ; reg: 0x003, bit: 5
1e43:  2000  call    0x0000
1e44:  0879  movf    (Common_RAM + 9), W                    ; reg: 0x079

label_369:                                                  ; address: 0x1e45

1e45:  00fa  movwf   (Common_RAM + 10)                      ; reg: 0x07a
1e46:  087a  movf    (Common_RAM + 10), W                   ; reg: 0x07a
1e47:  024b  subwf   0x4b, W                                ; reg: 0x04b
1e48:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1e49:  2e5c  goto    0x065c
1e4a:  1d03  btfss   STATUS, Z                              ; reg: 0x003, bit: 2
1e4b:  2e50  goto    0x0650
1e4c:  0878  movf    (Common_RAM + 8), W                    ; reg: 0x078

label_370:                                                  ; address: 0x1e4d

1e4d:  024a  subwf   0x4a, W                                ; reg: 0x04a
1e4e:  1c03  btfss   STATUS, C                              ; reg: 0x003, bit: 0
1e4f:  2e5c  goto    0x065c
1e50:  01cb  clrf    0x4b                                   ; reg: 0x04b
1e51:  01ca  clrf    0x4a                                   ; reg: 0x04a
1e52:  120a  bcf     PCLATH, 0x4                            ; reg: 0x00a
1e53:  27d3  call    0x07d3
1e54:  160a  bsf     PCLATH, 0x4                            ; reg: 0x00a
1e55:  308f  movlw   0x8f
1e56:  05cc  andwf   0x4c, F                                ; reg: 0x04c
1e57:  3050  movlw   0x50
1e58:  04cc  iorwf   0x4c, F                                ; reg: 0x04c
1e59:  084c  movf    0x4c, W                                ; reg: 0x04c
1e5a:  3907  andlw   0x07
1e5b:  00f5  movwf   (Common_RAM + 5)                       ; reg: 0x075
1e5c:  2e5d  goto    0x065d

label_371:                                                  ; address: 0x1e5d

1e5d:  2899  goto    0x0099
1e5e:  0063  sleep
