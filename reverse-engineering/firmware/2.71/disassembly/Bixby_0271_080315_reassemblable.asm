        processor p16f877a
        radix dec

        include p16f877a.inc

; The recognition of labels and registers is not always good, therefore
; be treated cautiously the results.

        CONFIG  FOSC  = HS
        CONFIG  WDTE  = OFF
        CONFIG  PWRTE = ON
        CONFIG  BOREN = ON
        CONFIG  LVP   = OFF
        CONFIG  CPD   = OFF
        CONFIG  WRT   = OFF
        CONFIG  DEBUG = OFF
        CONFIG  CP    = OFF

        __idlocs 0x4302

;===============================================================================
; DATA address definitions

Common_RAM      equ     0x0070                              ; size: 16 bytes

;===============================================================================
; CODE area

        ; code

        org     __CODE_START                                ; address: 0x0000

vector_reset:                                               ; address: 0x0000

        movlw   0x18
        movwf   PCLATH                                      ; reg: 0x00a
        goto    label_004
        nop

vector_int:                                                 ; address: 0x0004

        movwf   (Common_RAM + 15)                           ; reg: 0x07f
        swapf   STATUS, W                                   ; reg: 0x003
        clrf    STATUS                                      ; reg: 0x003
        movwf   0x21                                        ; reg: 0x021
        movf    PCLATH, W                                   ; reg: 0x00a
        movwf   0x20                                        ; reg: 0x020
        clrf    PCLATH                                      ; reg: 0x00a
        movf    FSR, W                                      ; reg: 0x004
        movwf   0x22                                        ; reg: 0x022
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        movwf   0x23                                        ; reg: 0x023
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x24                                        ; reg: 0x024
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x25                                        ; reg: 0x025
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x26                                        ; reg: 0x026
        movf    (Common_RAM + 11), W                        ; reg: 0x07b
        movwf   0x27                                        ; reg: 0x027
        bcf     STATUS, IRP                                 ; reg: 0x003, bit: 7
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   INTCON, INTE                                ; reg: 0x00b, bit: 4
        goto    label_002
        btfsc   INTCON, INTF                                ; reg: 0x00b, bit: 1
        goto    label_006

label_002:                                                  ; address: 0x001d

        movlw   0x8c
        movwf   FSR                                         ; reg: 0x004
        btfss   INDF, 0x5                                   ; reg: 0x000
        goto    label_003
        btfsc   PIR1, RCIF                                  ; reg: 0x00c, bit: 5
        goto    label_007

label_003:                                                  ; address: 0x0023

        movlw   0x8c
        movwf   FSR                                         ; reg: 0x004

label_004:                                                  ; address: 0x0025

        btfss   INDF, 0x1                                   ; reg: 0x000
        goto    label_005
        btfsc   PIR1, TMR2IF                                ; reg: 0x00c, bit: 1
        goto    label_008

label_005:                                                  ; address: 0x0029

        movf    0x22, W                                     ; reg: 0x022
        movwf   FSR                                         ; reg: 0x004
        movf    0x23, W                                     ; reg: 0x023
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        movf    0x24, W                                     ; reg: 0x024
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x25, W                                     ; reg: 0x025
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        movf    0x26, W                                     ; reg: 0x026
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    0x27, W                                     ; reg: 0x027
        movwf   (Common_RAM + 11)                           ; reg: 0x07b
        movf    0x20, W                                     ; reg: 0x020
        movwf   PCLATH                                      ; reg: 0x00a
        swapf   0x21, W                                     ; reg: 0x021
        movwf   STATUS                                      ; reg: 0x003
        swapf   (Common_RAM + 15), F                        ; reg: 0x07f
        swapf   (Common_RAM + 15), W                        ; reg: 0x07f
        retfie

label_006:                                                  ; address: 0x003c

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_034

label_007:                                                  ; address: 0x003f

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_009

label_008:                                                  ; address: 0x0042

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_043
        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x28
        retlw   0x2d
        retlw   0x32
        retlw   0x37
        retlw   0x3c
        retlw   0x41
        retlw   0x46
        retlw   0x4b
        retlw   0x50
        retlw   0x55
        retlw   0x5a

function_000:                                               ; address: 0x0054

        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x00
        retlw   0x00
        retlw   0x38
        retlw   0x04
        retlw   0x08
        retlw   0x07
        retlw   0x8c
        retlw   0x0a

function_001:                                               ; address: 0x0060

        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0xa0
        retlw   0x05
        retlw   0x40
        retlw   0x0b
        retlw   0x00
        retlw   0x0f
        retlw   0xe0
        retlw   0x10
        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x64
        retlw   0x70
        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x00
        retlw   0x00
        retlw   0x08
        retlw   0x07

function_002:                                               ; address: 0x007a

        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x20
        retlw   0x1c
        retlw   0x80
        retlw   0x16
        retlw   0xc0
        retlw   0x12
        retlw   0x12
        retlw   0x10
        retlw   0x10
        retlw   0x0e
        retlw   0x80
        retlw   0x0c
        retlw   0x40
        retlw   0x0b
        retlw   0x3a
        retlw   0x0a

function_003:                                               ; address: 0x008e

        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x00
        retlw   0x00
        retlw   0x68
        retlw   0x01
        retlw   0xd0
        retlw   0x02

function_004:                                               ; address: 0x0098

        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x10
        retlw   0x0e
        retlw   0x80
        retlw   0x0c
        retlw   0x10
        retlw   0x0e

function_005:                                               ; address: 0x00a2

        bcf     PCLATH, 0x0                                 ; reg: 0x00a
        bcf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        retlw   0x3c
        retlw   0x4b
        retlw   0x5a
        retlw   0x69
        retlw   0x78
        retlw   0x87
        retlw   0x96
        retlw   0xa5

label_009:                                                  ; address: 0x00ae

        btfss   PIR1, RCIF                                  ; reg: 0x00c, bit: 5
        goto    label_012
        movf    RCREG, W                                    ; reg: 0x01a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x65                                        ; reg: 0x065
        movf    0x65, W                                     ; reg: 0x065
        sublw   0x03
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_010
        clrf    0x41                                        ; reg: 0x041
        clrf    0x40                                        ; reg: 0x040
        goto    label_011

label_010:                                                  ; address: 0x00ba

        movf    0x41, W                                     ; reg: 0x041
        incf    0x41, F                                     ; reg: 0x041
        addlw   0xa3
        movwf   FSR                                         ; reg: 0x004
        movf    0x65, W                                     ; reg: 0x065
        movwf   INDF                                        ; reg: 0x000
        incf    0x40, F                                     ; reg: 0x040
        movf    0x41, W                                     ; reg: 0x041
        sublw   0x1c
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_011
        clrf    0x41                                        ; reg: 0x041
        movf    0x40, W                                     ; reg: 0x040
        sublw   0x1c
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_011
        clrf    0x41                                        ; reg: 0x041
        clrf    0x40                                        ; reg: 0x040

label_011:                                                  ; address: 0x00cc

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_009

label_012:                                                  ; address: 0x00ce

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_005

label_013:                                                  ; address: 0x00d1

        btfss   0x52, 0x1                                   ; reg: 0x052
        goto    label_014
        bcf     0x5d, 0x6                                   ; reg: 0x05d
        bsf     0x5d, 0x5                                   ; reg: 0x05d
        bsf     0x5d, 0x3                                   ; reg: 0x05d
        bcf     0x30, 0x3                                   ; reg: 0x030
        goto    label_023

label_014:                                                  ; address: 0x00d8

        btfss   0x52, 0x0                                   ; reg: 0x052
        goto    label_015
        bsf     0x43, 0x5                                   ; reg: 0x043
        bcf     0x50, 0x5                                   ; reg: 0x050
        bsf     0x5d, 0x6                                   ; reg: 0x05d
        bcf     0x5d, 0x5                                   ; reg: 0x05d
        bcf     0x5d, 0x3                                   ; reg: 0x05d
        goto    label_023

label_015:                                                  ; address: 0x00e0

        btfsc   0x52, 0x2                                   ; reg: 0x052
        goto    label_016
        btfss   0x52, 0x3                                   ; reg: 0x052
        goto    label_023

label_016:                                                  ; address: 0x00e4

        btfsc   0x52, 0x5                                   ; reg: 0x052
        goto    label_018
        decfsz  0x55, W                                     ; reg: 0x055
        goto    label_017
        goto    label_018

label_017:                                                  ; address: 0x00e9

        movf    0x55, W                                     ; reg: 0x055
        sublw   0x04
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_020

label_018:                                                  ; address: 0x00ed

        btfss   0x52, 0x2                                   ; reg: 0x052
        goto    label_019
        movf    0x5d, W                                     ; reg: 0x05d
        andlw   0x07
        sublw   0x06
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_019
        incf    0x5d, F                                     ; reg: 0x05d

label_019:                                                  ; address: 0x00f5

        btfss   0x52, 0x3                                   ; reg: 0x052
        goto    label_020
        movf    0x5d, W                                     ; reg: 0x05d
        andlw   0x07
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_020
        decf    0x5d, F                                     ; reg: 0x05d

label_020:                                                  ; address: 0x00fc

        decfsz  0x55, W                                     ; reg: 0x055
        goto    label_021
        incf    0x55, F                                     ; reg: 0x055

label_021:                                                  ; address: 0x00ff

        movf    0x55, W                                     ; reg: 0x055
        sublw   0x04
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_022
        movlw   0x02
        movwf   0x55                                        ; reg: 0x055

label_022:                                                  ; address: 0x0105

        movf    0x4c, W                                     ; reg: 0x04c
        xorwf   0x5d, W                                     ; reg: 0x05d
        andlw   0x07
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_023
        bsf     0x5d, 0x4                                   ; reg: 0x05d

label_023:                                                  ; address: 0x010b

        btfsc   0x52, 0x5                                   ; reg: 0x052
        goto    label_024
        btfss   0x52, 0x4                                   ; reg: 0x052
        goto    label_025

label_024:                                                  ; address: 0x010f

        clrf    0x52                                        ; reg: 0x052

label_025:                                                  ; address: 0x0110

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_033

label_026:                                                  ; address: 0x0113

        btfss   0x52, 0x4                                   ; reg: 0x052
        goto    label_027
        bcf     0x52, 0x4                                   ; reg: 0x052
        bsf     0x52, 0x5                                   ; reg: 0x052
        goto    label_028

label_027:                                                  ; address: 0x0118

        movlw   0x04
        movwf   PORTD                                       ; reg: 0x008
        bcf     0x52, 0x0                                   ; reg: 0x052
        btfss   PORTD, RD3                                  ; reg: 0x008, bit: 3
        bsf     0x52, 0x0                                   ; reg: 0x052
        movlw   0x24
        movwf   PORTD                                       ; reg: 0x008
        bcf     0x52, 0x1                                   ; reg: 0x052
        btfss   PORTD, RD3                                  ; reg: 0x008, bit: 3
        bsf     0x52, 0x1                                   ; reg: 0x052
        movlw   0x44
        movwf   PORTD                                       ; reg: 0x008
        bcf     0x52, 0x2                                   ; reg: 0x052
        btfss   PORTD, RD3                                  ; reg: 0x008, bit: 3
        bsf     0x52, 0x2                                   ; reg: 0x052
        movlw   0x64
        movwf   PORTD                                       ; reg: 0x008
        bcf     0x52, 0x3                                   ; reg: 0x052
        btfss   PORTD, RD3                                  ; reg: 0x008, bit: 3
        bsf     0x52, 0x3                                   ; reg: 0x052

label_028:                                                  ; address: 0x012c

        btfss   0x51, 0x3                                   ; reg: 0x051
        goto    label_029
        movf    0x52, W                                     ; reg: 0x052
        iorwf   0x53, F                                     ; reg: 0x053
        goto    label_033

label_029:                                                  ; address: 0x0131

        movf    0x53, W                                     ; reg: 0x053
        subwf   0x52, W                                     ; reg: 0x052
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_030
        incf    0x54, F                                     ; reg: 0x054
        goto    label_031

label_030:                                                  ; address: 0x0137

        clrf    0x54                                        ; reg: 0x054
        clrf    0x55                                        ; reg: 0x055
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x53                                        ; reg: 0x053

label_031:                                                  ; address: 0x013b

        btfss   0x52, 0x5                                   ; reg: 0x052
        goto    label_032
        movlw   0xfc
        movwf   0x54                                        ; reg: 0x054

label_032:                                                  ; address: 0x013f

        movf    0x54, W                                     ; reg: 0x054
        andlw   0xfc
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_033
        goto    label_013

label_033:                                                  ; address: 0x0144

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_035

label_034:                                                  ; address: 0x0147

        goto    label_026

label_035:                                                  ; address: 0x0148

        clrf    0x32                                        ; reg: 0x032
        clrf    0x31                                        ; reg: 0x031
        bsf     0x4c, 0x7                                   ; reg: 0x04c
        movf    (Common_RAM + 1), W                         ; reg: 0x071
        iorwf   (Common_RAM + 2), W                         ; reg: 0x072
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_036
        movf    (Common_RAM + 1), W                         ; reg: 0x071
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        decf    (Common_RAM + 2), F                         ; reg: 0x072
        decf    (Common_RAM + 1), F                         ; reg: 0x071

label_036:                                                  ; address: 0x0153

        movlw   0x02
        xorwf   0x30, F                                     ; reg: 0x030
        btfss   PORTB, RB1                                  ; reg: 0x006, bit: 1
        goto    label_037
        incf    0x46, F                                     ; reg: 0x046
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        incf    0x47, F                                     ; reg: 0x047

label_037:                                                  ; address: 0x015a

        clrf    TMR2                                        ; reg: 0x011
        bcf     PIR1, TMR2IF                                ; reg: 0x00c, bit: 1
        incf    0x35, F                                     ; reg: 0x035
        btfss   0x35, 0x5                                   ; reg: 0x035
        goto    label_038
        movlw   0x82
        movwf   0x35                                        ; reg: 0x035
        movf    TMR0, W                                     ; reg: 0x001
        btfsc   INTCON, T0IF                                ; reg: 0x00b, bit: 2
        movlw   0xff
        movwf   0x34                                        ; reg: 0x034
        clrf    TMR0                                        ; reg: 0x001
        bcf     INTCON, T0IF                                ; reg: 0x00b, bit: 2

label_038:                                                  ; address: 0x0167

        bcf     PORTB, RB3                                  ; reg: 0x006, bit: 3
        movlw   0x00
        btfsc   0x30, 0x1                                   ; reg: 0x030
        movlw   0x01
        andlw   0x01
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_041
        movf    0x29, W                                     ; reg: 0x029
        addwf   0x2a, F                                     ; reg: 0x02a
        movf    0x2a, W                                     ; reg: 0x02a
        sublw   0x63
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_039
        movlw   0x64
        subwf   0x2a, F                                     ; reg: 0x02a
        bsf     0x56, 0x3                                   ; reg: 0x056
        bsf     PORTC, RC5                                  ; reg: 0x007, bit: 5
        movlw   0x60
        movwf   PORTD                                       ; reg: 0x008
        bsf     PORTD, RD2                                  ; reg: 0x008, bit: 2
        bcf     0x51, 0x5                                   ; reg: 0x051
        goto    label_040

label_039:                                                  ; address: 0x017d

        btfss   0x51, 0x5                                   ; reg: 0x051
        goto    label_040
        bcf     0x56, 0x3                                   ; reg: 0x056
        bcf     PORTC, RC5                                  ; reg: 0x007, bit: 5
        movlw   0x60
        movwf   PORTD                                       ; reg: 0x008
        bsf     PORTD, RD2                                  ; reg: 0x008, bit: 2
        bcf     0x51, 0x5                                   ; reg: 0x051

label_040:                                                  ; address: 0x0185

        goto    label_042

label_041:                                                  ; address: 0x0186

        bsf     0x51, 0x5                                   ; reg: 0x051

label_042:                                                  ; address: 0x0187

        bcf     INTCON, INTF                                ; reg: 0x00b, bit: 1
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_005

label_043:                                                  ; address: 0x018b

        incfsz  0x31, F                                     ; reg: 0x031
        goto    label_044
        incfsz  0x32, W                                     ; reg: 0x032
        movwf   0x32                                        ; reg: 0x032

label_044:                                                  ; address: 0x018f

        btfss   0x4c, 0x7                                   ; reg: 0x04c
        goto    label_045
        bcf     0x4c, 0x7                                   ; reg: 0x04c
        movf    0x37, W                                     ; reg: 0x037
        movwf   0x38                                        ; reg: 0x038
        goto    label_046

label_045:                                                  ; address: 0x0195

        movf    0x38, F                                     ; reg: 0x038
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        decfsz  0x38, F                                     ; reg: 0x038
        goto    label_046
        bsf     PORTB, RB3                                  ; reg: 0x006, bit: 3

label_046:                                                  ; address: 0x019a

        bcf     PIR1, TMR2IF                                ; reg: 0x00c, bit: 1
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_005

function_006:                                               ; address: 0x019e

        movlw   0x01
        movwf   (Common_RAM + 4)                            ; reg: 0x074
        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6

label_047:                                                  ; address: 0x01a1

        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    label_047
        movlw   0x1f
        andwf   PORTD, F                                    ; reg: 0x008

label_048:                                                  ; address: 0x01a6

        movf    (Common_RAM + 4), F                         ; reg: 0x074
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_050
        bsf     PORTC, RC5                                  ; reg: 0x007, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        andwf   (Common_RAM + 4), W                         ; reg: 0x074
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_049
        bcf     PORTC, RC5                                  ; reg: 0x007, bit: 5

label_049:                                                  ; address: 0x01af

        bcf     PORTC, RC2                                  ; reg: 0x007, bit: 2
        bsf     PORTC, RC2                                  ; reg: 0x007, bit: 2
        movlw   0x20
        addwf   PORTD, F                                    ; reg: 0x008
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 4), F                         ; reg: 0x074
        goto    label_048

label_050:                                                  ; address: 0x01b6

        movlw   0xc0
        iorwf   INTCON, F                                   ; reg: 0x00b
        retlw   0x00

label_051:                                                  ; address: 0x01b9

        movlw   0x07
        movwf   0x2d                                        ; reg: 0x02d
        clrf    PORTA                                       ; reg: 0x005
        clrf    PORTB                                       ; reg: 0x006
        clrf    PORTC                                       ; reg: 0x007
        movlw   0x04
        movwf   PORTE                                       ; reg: 0x009
        clrf    0x48                                        ; reg: 0x048
        call    function_006
        clrf    0x49                                        ; reg: 0x049
        clrf    0x3b                                        ; reg: 0x03b
        clrf    0x3c                                        ; reg: 0x03c
        clrf    0x55                                        ; reg: 0x055
        clrf    0x54                                        ; reg: 0x054
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        clrf    0x5d                                        ; reg: 0x05d
        clrf    0x53                                        ; reg: 0x053
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x52                                        ; reg: 0x052
        clrf    0x51                                        ; reg: 0x051
        clrf    0x57                                        ; reg: 0x057
        clrf    0x30                                        ; reg: 0x030
        movlw   0xdc
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_058

function_007:                                               ; address: 0x01d5

        bcf     PORTB, RB3                                  ; reg: 0x006, bit: 3
        clrf    0x33                                        ; reg: 0x033
        clrf    0x38                                        ; reg: 0x038
        clrf    0x37                                        ; reg: 0x037
        clrf    0x35                                        ; reg: 0x035
        clrf    0x34                                        ; reg: 0x034
        retlw   0x00

function_008:                                               ; address: 0x01dc

        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6

label_052:                                                  ; address: 0x01dd

        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    label_052
        movlw   0x1f
        andwf   PORTD, F                                    ; reg: 0x008
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054

label_053:                                                  ; address: 0x01e5

        movf    0x54, F                                     ; reg: 0x054
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PORTC, RC5                                  ; reg: 0x007, bit: 5
        movf    0x56, W                                     ; reg: 0x056
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        andwf   0x54, W                                     ; reg: 0x054
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_054
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PORTC, RC5                                  ; reg: 0x007, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_054:                                                  ; address: 0x01f2

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PORTD, RD2                                  ; reg: 0x008, bit: 2
        bsf     PORTD, RD2                                  ; reg: 0x008, bit: 2
        movlw   0x20
        addwf   PORTD, F                                    ; reg: 0x008
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        rlf     0x54, F                                     ; reg: 0x054
        goto    label_053

label_055:                                                  ; address: 0x01fb

        movlw   0xc0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        iorwf   INTCON, F                                   ; reg: 0x00b
        retlw   0x00

label_056:                                                  ; address: 0x01ff

        movlw   0xbf
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   TMR0                                        ; reg: 0x001
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    TMR0                                        ; reg: 0x001
        bcf     INTCON, T0IF                                ; reg: 0x00b, bit: 2
        movlw   0x3f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   PORTA                                       ; reg: 0x005
        movlw   0xd1
        movwf   PORTB                                       ; reg: 0x006
        movlw   0x80
        movwf   PORTC                                       ; reg: 0x007

label_057:                                                  ; address: 0x020c

        movlw   0x1b
        movwf   PORTD                                       ; reg: 0x008
        bsf     PORTE, RE0                                  ; reg: 0x009, bit: 0
        bsf     PORTE, RE1                                  ; reg: 0x009, bit: 1
        bcf     PORTE, RE2                                  ; reg: 0x009, bit: 2
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_051

label_058:                                                  ; address: 0x0213

        call    function_007
        movlw   0x74
        movwf   CCPR1L                                      ; reg: 0x015
        movlw   0xc6
        movwf   CCPR1H                                      ; reg: 0x016
        movlw   0x0b
        movwf   CCP1CON                                     ; reg: 0x017
        movlw   0x31
        movwf   T1CON                                       ; reg: 0x010
        clrf    TMR1H                                       ; reg: 0x00f
        clrf    TMR1L                                       ; reg: 0x00e
        movlw   0x09
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   ADCON0                                      ; reg: 0x01f
        movlw   0x81
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   ADCON0                                      ; reg: 0x01f
        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        iorlw   0x04
        movwf   T2CON                                       ; reg: 0x012
        movlw   0x42
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   T2CON                                       ; reg: 0x012
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     INTCON, INTE                                ; reg: 0x00b, bit: 4
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PIR1, TMR2IF                                ; reg: 0x00c, bit: 1
        movlw   0xc0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        iorwf   INTCON, F                                   ; reg: 0x00b
        movlw   0xd1
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   PORTB                                       ; reg: 0x006
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x56                                        ; reg: 0x056
        call    function_008
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_061

label_059:                                                  ; address: 0x023b

        movf    RCREG, W                                    ; reg: 0x01a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x23                                        ; reg: 0x023
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     RCSTA, CREN                                 ; reg: 0x018, bit: 4
        bsf     RCSTA, CREN                                 ; reg: 0x018, bit: 4
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x23                                        ; reg: 0x023
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_062

label_060:                                                  ; address: 0x0247

        goto    label_056

label_061:                                                  ; address: 0x0248

        goto    label_059

label_062:                                                  ; address: 0x0249

        movlw   0xdc
        movwf   0x5a                                        ; reg: 0x05a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x42                                        ; reg: 0x042
        clrf    0x20                                        ; reg: 0x020
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     0x51, 0x3                                   ; reg: 0x051
        bcf     (Common_RAM + 14), 0x0                      ; reg: 0x07e
        clrf    0x4d                                        ; reg: 0x04d
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_231

function_009:                                               ; address: 0x0255

        clrf    0x61                                        ; reg: 0x061
        clrf    0x62                                        ; reg: 0x062
        clrf    0x6b                                        ; reg: 0x06b
        clrf    0x6d                                        ; reg: 0x06d
        clrf    0x6e                                        ; reg: 0x06e
        movlw   0xf0
        andwf   (Common_RAM + 14), F                        ; reg: 0x07e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x48                                        ; reg: 0x048
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_294
        movlw   0x63
        addwf   0x48, W                                     ; reg: 0x048
        movwf   FSR                                         ; reg: 0x004
        clrf    INDF                                        ; reg: 0x000
        incf    0x48, F                                     ; reg: 0x048
        goto    label_292
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_010:                                               ; address: 0x026a

        bsf     0x56, 0x5                                   ; reg: 0x056
        call    function_063
        retlw   0x00

function_011:                                               ; address: 0x026d

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, F                                     ; reg: 0x053
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x027a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   0x2d, 0x1                                   ; reg: 0x02d
        goto    0x0276
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x027a
        call    0x026a
        bsf     PORTC, RC0                                  ; reg: 0x007, bit: 0
        goto    0x027c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PORTC, RC0                                  ; reg: 0x007, bit: 0
        retlw   0x00
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, F                                     ; reg: 0x053
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x028a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   0x2d, 0x0                                   ; reg: 0x02d
        goto    0x0286
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x028a
        call    0x026a
        bsf     PORTC, RC1                                  ; reg: 0x007, bit: 1
        goto    0x028c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PORTC, RC1                                  ; reg: 0x007, bit: 1
        retlw   0x00

function_012:                                               ; address: 0x028d

        bcf     0x2d, 0x7                                   ; reg: 0x02d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x026d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x027d
        retlw   0x00
        movlw   0x0f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        andwf   0x58, F                                     ; reg: 0x058
        movf    0x58, W                                     ; reg: 0x058
        sublw   0x09
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x02a2
        movlw   0x57
        addwf   0x58, W                                     ; reg: 0x058
        movwf   0x59                                        ; reg: 0x059
        goto    0x02a5
        movlw   0x30
        addwf   0x58, W                                     ; reg: 0x058
        movwf   0x59                                        ; reg: 0x059
        movf    0x59, W                                     ; reg: 0x059
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    0x02ab
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x02a6
        movwf   TXREG                                       ; reg: 0x019
        retlw   0x00

function_013:                                               ; address: 0x02ad

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        swapf   0x56, W                                     ; reg: 0x056
        movwf   0x57                                        ; reg: 0x057
        movlw   0x0f
        andwf   0x57, F                                     ; reg: 0x057
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x58                                        ; reg: 0x058
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0297
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x56, W                                     ; reg: 0x056
        movwf   0x58                                        ; reg: 0x058
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_063:                                                  ; address: 0x02ba

        call    0x0297
        retlw   0x00

function_014:                                               ; address: 0x02bc

        btfsc   0x51, 0x3                                   ; reg: 0x051
        goto    0x02d4
        movlw   0x44
        btfss   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    0x02bf
        movwf   TXREG                                       ; reg: 0x019
        movlw   0x57
        btfss   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    0x02c3
        movwf   TXREG                                       ; reg: 0x019
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x56                                        ; reg: 0x056
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02ad
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x56                                        ; reg: 0x056
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02ad
        movlw   0x0a
        btfss   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    0x02d1
        movwf   TXREG                                       ; reg: 0x019
        retlw   0x00
        bcf     SSPCON, WCOL                                ; reg: 0x014, bit: 7
        bcf     PIR1, SSPIF                                 ; reg: 0x00c, bit: 3
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x55, W                                     ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   SSPBUF                                      ; reg: 0x013
        movlw   0x02
        btfsc   SSPCON, WCOL                                ; reg: 0x014, bit: 7
        goto    0x02e5
        btfss   PIR1, SSPIF                                 ; reg: 0x00c, bit: 3
        goto    0x02de
        movlw   0x00
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   TMR2, 0x6                                   ; reg: 0x011
        movlw   0x01
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        retlw   0x00
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     TMR2, 0x3                                   ; reg: 0x011
        btfsc   TMR2, 0x3                                   ; reg: 0x011
        goto    0x02e9
        btfsc   (Common_RAM + 7), 0x0                       ; reg: 0x077
        bcf     TMR2, 0x5                                   ; reg: 0x011
        btfss   (Common_RAM + 7), 0x0                       ; reg: 0x077
        bsf     TMR2, 0x5                                   ; reg: 0x011
        bsf     TMR2, 0x4                                   ; reg: 0x011
        btfsc   TMR2, 0x4                                   ; reg: 0x011
        goto    0x02f0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    SSPBUF, W                                   ; reg: 0x013
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        retlw   0x00

function_015:                                               ; address: 0x02f6

        rlf     0x2c, W                                     ; reg: 0x02c
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        movlw   0xf8
        andwf   (Common_RAM + 7), F                         ; reg: 0x077
        movf    ADCON0, W                                   ; reg: 0x01f
        andlw   0xc7
        iorwf   (Common_RAM + 7), W                         ; reg: 0x077
        movwf   ADCON0                                      ; reg: 0x01f
        movlw   0x53
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        decfsz  (Common_RAM + 7), F                         ; reg: 0x077
        goto    0x0302
        movf    0x2c, F                                     ; reg: 0x02c
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0307
        decfsz  0x2c, W                                     ; reg: 0x02c
        goto    0x0310
        btfsc   PORTB, RB1                                  ; reg: 0x006, bit: 1
        goto    0x0310
        bsf     ADCON0, GO                                  ; reg: 0x01f, bit: 2
        btfsc   ADCON0, GO                                  ; reg: 0x01f, bit: 2
        goto    0x030c
        movf    ADRESH, W                                   ; reg: 0x01e
        movwf   0x57                                        ; reg: 0x057
        movf    0x2c, W                                     ; reg: 0x02c
        sublw   0x02
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x033e
        bsf     ADCON0, GO                                  ; reg: 0x01f, bit: 2
        btfsc   ADCON0, GO                                  ; reg: 0x01f, bit: 2
        goto    0x0315
        movf    ADRESH, W                                   ; reg: 0x01e
        movwf   0x58                                        ; reg: 0x058
        movf    0x58, W                                     ; reg: 0x058
        sublw   0x14
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0329
        btfsc   0x56, 0x5                                   ; reg: 0x056
        goto    0x0321
        incf    0x6f, F                                     ; reg: 0x06f
        goto    0x0326
        movf    0x6f, W                                     ; reg: 0x06f
        sublw   0x06
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0326
        clrf    0x6f                                        ; reg: 0x06f
        btfsc   0x2d, 0x7                                   ; reg: 0x02d
        goto    0x0329
        incf    0x6f, F                                     ; reg: 0x06f
        movf    0x6f, W                                     ; reg: 0x06f
        sublw   0x06
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x033e
        call    0x028d
        call    0x026a
        bsf     0x4f, 0x6                                   ; reg: 0x04f
        bsf     0x4f, 0x0                                   ; reg: 0x04f
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        movlw   0x1c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x58, W                                     ; reg: 0x058
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        movlw   0x0c
        movwf   0x6f                                        ; reg: 0x06f
        movf    0x2c, W                                     ; reg: 0x02c
        sublw   0x03
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0347
        bsf     ADCON0, GO                                  ; reg: 0x01f, bit: 2
        btfsc   ADCON0, GO                                  ; reg: 0x01f, bit: 2
        goto    0x0343
        movf    ADRESH, W                                   ; reg: 0x01e
        movwf   0x2e                                        ; reg: 0x02e
        movf    0x2c, W                                     ; reg: 0x02c
        sublw   0x04
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0350
        bsf     ADCON0, GO                                  ; reg: 0x01f, bit: 2
        btfsc   ADCON0, GO                                  ; reg: 0x01f, bit: 2
        goto    0x034c
        movf    ADRESH, W                                   ; reg: 0x01e
        movwf   0x2f                                        ; reg: 0x02f
        movf    0x2c, W                                     ; reg: 0x02c

label_064:                                                  ; address: 0x0351

        sublw   0x05
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x03b2
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x22, W                                     ; reg: 0x022
        movwf   0x53                                        ; reg: 0x053
        bsf     TMR2, 0x0                                   ; reg: 0x011
        btfsc   TMR2, 0x0                                   ; reg: 0x011
        goto    0x0358
        movlw   0x9a
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02d5
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02d5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     TMR2, 0x2                                   ; reg: 0x011
        btfsc   TMR2, 0x2                                   ; reg: 0x011
        goto    0x0365
        bsf     TMR2, 0x0                                   ; reg: 0x011
        btfsc   TMR2, 0x0                                   ; reg: 0x011
        goto    0x0368
        movlw   0x9b
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02d5
        movlw   0x01
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        call    0x02e7
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bsf     TMR2, 0x2                                   ; reg: 0x011
        btfsc   TMR2, 0x2                                   ; reg: 0x011
        goto    0x0375
        movf    0x54, W                                     ; reg: 0x054
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        btfss   (Common_RAM + 8), 0x6                       ; reg: 0x078
        goto    0x0357
        bsf     TMR2, 0x0                                   ; reg: 0x011
        btfsc   TMR2, 0x0                                   ; reg: 0x011
        goto    0x037c
        movlw   0x9a
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02d5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02d5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     TMR2, 0x2                                   ; reg: 0x011
        btfsc   TMR2, 0x2                                   ; reg: 0x011
        goto    0x0388
        bsf     TMR2, 0x0                                   ; reg: 0x011
        btfsc   TMR2, 0x0                                   ; reg: 0x011
        goto    0x038b
        movlw   0x9b
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02d5
        movlw   0x01
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        call    0x02e7
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x22                                        ; reg: 0x022
        bsf     TMR2, 0x2                                   ; reg: 0x011
        btfsc   TMR2, 0x2                                   ; reg: 0x011
        goto    0x0398
        movlw   0x01
        addwf   0x53, W                                     ; reg: 0x053
        xorlw   0x80
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        movf    0x22, W                                     ; reg: 0x022
        xorlw   0x80
        subwf   (Common_RAM + 7), W                         ; reg: 0x077
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03a5
        incf    0x22, F                                     ; reg: 0x022
        goto    0x03b1
        movlw   0x01
        subwf   0x53, W                                     ; reg: 0x053
        xorlw   0x80
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        movf    0x22, W                                     ; reg: 0x022
        xorlw   0x80
        subwf   (Common_RAM + 7), W                         ; reg: 0x077
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x03b1
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03b1
        decf    0x22, F                                     ; reg: 0x022
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    0x2c, F                                     ; reg: 0x02c
        movf    0x2c, W                                     ; reg: 0x02c
        sublw   0x05
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03b8
        clrf    0x2c                                        ; reg: 0x02c
        retlw   0x00

function_016:                                               ; address: 0x03b9

        movlw   0x10
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        clrf    (Common_RAM + 7)                            ; reg: 0x077
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        rrf     0x57, F                                     ; reg: 0x057
        rrf     0x56, F                                     ; reg: 0x056
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03c8
        movf    0x58, W                                     ; reg: 0x058
        addwf   (Common_RAM + 7), F                         ; reg: 0x077
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    (Common_RAM + 10), F                        ; reg: 0x07a
        movf    0x59, W                                     ; reg: 0x059
        addwf   (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 7), F                         ; reg: 0x077
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        rrf     (Common_RAM + 8), F                         ; reg: 0x078
        decfsz  0x5a, F                                     ; reg: 0x05a
        goto    0x03be
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_017:                                               ; address: 0x03d0

        btfsc   0x51, 0x2                                   ; reg: 0x051
        goto    0x03d6
        movlw   0x30
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x5a, F                                     ; reg: 0x05a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x5a, W                                     ; reg: 0x05a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, RD                                  ; reg: 0x18c, bit: 0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    EEDATA, W                                   ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   0x5b                                        ; reg: 0x0db
        movf    0x5b, W                                     ; reg: 0x0db
        movwf   0x78                                        ; reg: 0x0f8
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_018:                                               ; address: 0x03e7

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x61                                        ; reg: 0x061
        clrf    0x5f                                        ; reg: 0x05f
        clrf    0x5e                                        ; reg: 0x05e
        movlw   0x80
        movwf   0x60                                        ; reg: 0x060
        clrf    0x62                                        ; reg: 0x062
        movf    0x62, W                                     ; reg: 0x062
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x041c
        movf    0x5c, W                                     ; reg: 0x05c
        andwf   0x60, W                                     ; reg: 0x060
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        iorwf   (Common_RAM + 10), W                        ; reg: 0x07a
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0400
        movf    0x5a, W                                     ; reg: 0x05a
        addwf   0x5e, F                                     ; reg: 0x05e
        movf    0x5b, W                                     ; reg: 0x05b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x5b, W                                     ; reg: 0x05b
        addwf   0x5f, F                                     ; reg: 0x05f
        movf    0x5a, W                                     ; reg: 0x05a
        andlw   0x01
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        iorwf   (Common_RAM + 10), W                        ; reg: 0x07a
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x040c
        movf    0x60, W                                     ; reg: 0x060
        addwf   0x61, F                                     ; reg: 0x061
        movf    0x60, W                                     ; reg: 0x060
        addwf   0x61, F                                     ; reg: 0x061
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     0x5b, F                                     ; reg: 0x05b
        rrf     0x5a, F                                     ; reg: 0x05a
        movf    0x61, W                                     ; reg: 0x061
        sublw   0x80
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0418
        movlw   0x80
        subwf   0x61, F                                     ; reg: 0x061
        incf    0x5a, F                                     ; reg: 0x05a
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        incf    0x5b, F                                     ; reg: 0x05b
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     0x60, F                                     ; reg: 0x060
        incf    0x62, F                                     ; reg: 0x062
        goto    0x03ee
        movf    0x5e, W                                     ; reg: 0x05e
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x5f, W                                     ; reg: 0x05f
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_019:                                               ; address: 0x0422

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x59                                        ; reg: 0x059
        btfss   (Common_RAM + 14), 0x0                      ; reg: 0x07e
        goto    0x0470
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x5a                                        ; reg: 0x05a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x58                                        ; reg: 0x058
        movf    0x54, W                                     ; reg: 0x054
        sublw   0x07
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0436
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     0x54, F                                     ; reg: 0x054
        rrf     0x53, F                                     ; reg: 0x053
        incf    0x59, F                                     ; reg: 0x059
        goto    0x042d
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x58, W                                     ; reg: 0x058
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x57                                        ; reg: 0x057
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x56                                        ; reg: 0x056
        movf    0x57, W                                     ; reg: 0x057
        sublw   0x05
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0454
        xorlw   0xff
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x044f
        movf    0x56, W                                     ; reg: 0x056
        sublw   0x3d
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0454
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     0x57, F                                     ; reg: 0x057
        rrf     0x56, F                                     ; reg: 0x056
        incf    0x59, F                                     ; reg: 0x059
        goto    0x0444
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x56, W                                     ; reg: 0x056
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0xa4
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x57                                        ; reg: 0x057
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x56                                        ; reg: 0x056
        movf    0x59, F                                     ; reg: 0x059
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x046a
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x56, F                                     ; reg: 0x056
        rlf     0x57, F                                     ; reg: 0x057
        decf    0x59, F                                     ; reg: 0x059
        goto    0x0462
        movf    0x56, W                                     ; reg: 0x056
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x57, W                                     ; reg: 0x057
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        goto    0x0475
        goto    0x0475
        movf    0x53, W                                     ; reg: 0x053
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x54, W                                     ; reg: 0x054
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        goto    0x0475
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_020:                                               ; address: 0x0477

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x57                                        ; reg: 0x057
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x56                                        ; reg: 0x056
        clrf    0x59                                        ; reg: 0x059
        movlw   0x18
        movwf   0x58                                        ; reg: 0x058
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03b9
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4d                                        ; reg: 0x04d
        btfss   (Common_RAM + 14), 0x0                      ; reg: 0x07e
        goto    0x049b
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x54                                        ; reg: 0x054
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x53                                        ; reg: 0x053
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0422
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x50                                        ; reg: 0x050
        movf    0x50, W                                     ; reg: 0x050
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x51, W                                     ; reg: 0x051
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        goto    0x04a0
        goto    0x04a0
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        goto    0x04a0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00
        clrf    (Common_RAM + 8)                            ; reg: 0x078
        clrf    (Common_RAM + 9)                            ; reg: 0x079
        clrf    (Common_RAM + 7)                            ; reg: 0x077
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x57, W                                     ; reg: 0x057
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04ad
        movf    0x56, W                                     ; reg: 0x056
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04c7
        movlw   0x10
        movwf   0x58                                        ; reg: 0x058
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x54, F                                     ; reg: 0x054
        rlf     0x55, F                                     ; reg: 0x055
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        rlf     (Common_RAM + 10), F                        ; reg: 0x07a
        movf    0x57, W                                     ; reg: 0x057
        subwf   (Common_RAM + 10), W                        ; reg: 0x07a
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04ba
        movf    0x56, W                                     ; reg: 0x056
        subwf   (Common_RAM + 7), W                         ; reg: 0x077
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04c3
        movf    0x56, W                                     ; reg: 0x056
        subwf   (Common_RAM + 7), F                         ; reg: 0x077
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        decf    (Common_RAM + 10), F                        ; reg: 0x07a
        movf    0x57, W                                     ; reg: 0x057
        subwf   (Common_RAM + 10), F                        ; reg: 0x07a
        bsf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 8), F                         ; reg: 0x078
        rlf     (Common_RAM + 9), F                         ; reg: 0x079
        decfsz  0x58, F                                     ; reg: 0x058
        goto    0x04af
        nop
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00
        btfss   PORTD, RD1                                  ; reg: 0x008, bit: 1
        goto    0x04ec
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        sublw   0x05
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04d4
        movlw   0x06
        movwf   0x53                                        ; reg: 0x053
        clrf    0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x2f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04ec
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        rrf     0x53, W                                     ; reg: 0x053
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        rrf     0x52, W                                     ; reg: 0x052
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        movlw   0x1f
        andwf   (Common_RAM + 10), F                        ; reg: 0x07a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        addwf   0x52, F                                     ; reg: 0x052
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 10), W                        ; reg: 0x07a
        addwf   0x53, F                                     ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   PORTD, RD4                                  ; reg: 0x008, bit: 4
        goto    0x0504
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x52, W                                     ; reg: 0x052
        iorwf   0x53, W                                     ; reg: 0x053
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0503
        rrf     0x53, W                                     ; reg: 0x053
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        rrf     0x52, W                                     ; reg: 0x052
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        movlw   0x1f
        andwf   (Common_RAM + 10), F                        ; reg: 0x07a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        addwf   0x52, F                                     ; reg: 0x052
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 10), W                        ; reg: 0x07a
        addwf   0x53, F                                     ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x50, 0x4                                   ; reg: 0x050
        goto    0x051d
        movlw   0x6c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x55                                        ; reg: 0x055
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x54                                        ; reg: 0x054
        clrf    0x57                                        ; reg: 0x057
        movlw   0x18
        movwf   0x56                                        ; reg: 0x056
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04a2
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x52                                        ; reg: 0x052
        movf    0x53, W                                     ; reg: 0x053
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0533
        clrf    0x53                                        ; reg: 0x053
        movlw   0xff
        movwf   0x52                                        ; reg: 0x052
        movf    0x52, W                                     ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x33, W                                     ; reg: 0x033
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x053d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, F                                     ; reg: 0x053
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0544
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x52, W                                     ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x33                                        ; reg: 0x033
        movlw   0xff
        movwf   0x3c                                        ; reg: 0x03c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_021:                                               ; address: 0x0546

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0x26
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x50                                        ; reg: 0x050
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x2e, W                                     ; reg: 0x02e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x50                                        ; reg: 0x050
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0x59
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x50, F                                     ; reg: 0x050
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 9), W                         ; reg: 0x079
        addwf   0x51, F                                     ; reg: 0x051
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x53                                        ; reg: 0x053
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04ca
        retlw   0x00

function_022:                                               ; address: 0x057c

        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x30
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0586
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, F                                     ; reg: 0x049
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x05a5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        call    0x00a2
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        addlw   0x40
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4c                                        ; reg: 0x04c
        clrf    0x4e                                        ; reg: 0x04e
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x4d                                        ; reg: 0x04d
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x4f                                        ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0477
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x4f                                        ; reg: 0x04f
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x4e                                        ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0546
        goto    0x05b0
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x20
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x05b0
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x53                                        ; reg: 0x053
        clrf    0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04ca
        retlw   0x00

function_023:                                               ; address: 0x05b1

        btfsc   0x51, 0x3                                   ; reg: 0x051
        goto    0x05cb
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x49                                        ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x057c
        movf    0x57, W                                     ; reg: 0x057
        sublw   0x13
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x05c0
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, F                                     ; reg: 0x048
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x05c9
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movlw   0x08
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movlw   0x34
        movwf   0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04ca
        goto    0x05cb
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x01d5
        retlw   0x00

function_024:                                               ; address: 0x05cc

        movlw   0xce
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x05e0
        movlw   0x03
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        clrf    (Common_RAM + 7)                            ; reg: 0x077
        decfsz  (Common_RAM + 7), F                         ; reg: 0x077
        goto    0x05d4
        decfsz  (Common_RAM + 8), F                         ; reg: 0x078
        goto    0x05d3
        movlw   0x3c
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        decfsz  (Common_RAM + 7), F                         ; reg: 0x077
        goto    0x05da
        nop
        nop
        decfsz  INDF, F                                     ; reg: 0x000
        goto    0x05d1
        retlw   0x00

label_065:                                                  ; address: 0x05e1

        movlw   0x01
        movwf   0x48                                        ; reg: 0x048
        call    0x019e
        movlw   0x0a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x05cc
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x48, F                                     ; reg: 0x048
        movf    0x48, F                                     ; reg: 0x048
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x05ef
        goto    0x05e3
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_069

label_066:                                                  ; address: 0x05f2

        movlw   0x80
        movwf   0x48                                        ; reg: 0x048

label_067:                                                  ; address: 0x05f4

        call    function_006
        movlw   0x0a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_024
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     0x48, F                                     ; reg: 0x048
        movf    0x48, F                                     ; reg: 0x048
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_068
        goto    label_067

label_068:                                                  ; address: 0x0600

        call    function_006
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_071

function_025:                                               ; address: 0x0604

        goto    label_065

label_069:                                                  ; address: 0x0605

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        call    function_006
        movlw   0x04
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049

label_070:                                                  ; address: 0x060d

        movlw   0xfa
        movwf   0x4e                                        ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_024
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        decfsz  0x49, F                                     ; reg: 0x049
        goto    label_070
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_066

label_071:                                                  ; address: 0x0616

        retlw   0x00

label_072:                                                  ; address: 0x0617

        movlw   0x02
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_025
        movlw   0x71
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_025
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_234

function_026:                                               ; address: 0x0624

        movf    0x43, W                                     ; reg: 0x043
        andlw   0x0f
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_367
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        sublw   0x01
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_366
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_365
        movf    0x52, W                                     ; reg: 0x052
        sublw   0x67
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_366
        movlw   0x01
        movwf   0x53                                        ; reg: 0x053
        movlw   0x68
        movwf   0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x52, W                                     ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x41, W                                     ; reg: 0x041
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_369
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x42, W                                     ; reg: 0x042
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_370
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x40                                        ; reg: 0x040
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x52, W                                     ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x3f                                        ; reg: 0x03f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x42                                        ; reg: 0x042
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x52, W                                     ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x41                                        ; reg: 0x041
        bcf     0x43, 0x5                                   ; reg: 0x043
        retlw   0x00

label_073:                                                  ; address: 0x0657

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0x26
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_064
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x52                                        ; reg: 0x052
        movlw   0x6e
        movwf   0x5a                                        ; reg: 0x05a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        btfss   (Common_RAM + 8), 0x0                       ; reg: 0x078
        goto    0x067f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x2e, W                                     ; reg: 0x02e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x52                                        ; reg: 0x052
        goto    0x0691
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x2f, W                                     ; reg: 0x02f
        sublw   0xff
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x52                                        ; reg: 0x052
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0x59
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x52, F                                     ; reg: 0x052
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 9), W                         ; reg: 0x079
        addwf   0x53, F                                     ; reg: 0x053
        movf    0x52, W                                     ; reg: 0x052
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x53, W                                     ; reg: 0x053
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_074

function_027:                                               ; address: 0x06a9

        bcf     PORTB, RB1                                  ; reg: 0x006, bit: 1
        movf    0x42, W                                     ; reg: 0x042
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x41, W                                     ; reg: 0x041
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_073

label_074:                                                  ; address: 0x06b3

        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x40                                        ; reg: 0x040
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x3f                                        ; reg: 0x03f
        movf    0x45, W                                     ; reg: 0x045
        subwf   0x40, W                                     ; reg: 0x040
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_076
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_075
        movf    0x3f, W                                     ; reg: 0x03f
        subwf   0x44, W                                     ; reg: 0x044
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_076

label_075:                                                  ; address: 0x06c1

        movf    0x44, W                                     ; reg: 0x044
        subwf   0x3f, W                                     ; reg: 0x03f
        movwf   0x3d                                        ; reg: 0x03d
        movf    0x40, W                                     ; reg: 0x040
        movwf   0x3e                                        ; reg: 0x03e
        movf    0x45, W                                     ; reg: 0x045
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x45, W                                     ; reg: 0x045
        subwf   0x3e, F                                     ; reg: 0x03e
        goto    label_077

label_076:                                                  ; address: 0x06cb

        clrf    0x3e                                        ; reg: 0x03e
        movlw   0x01
        movwf   0x3d                                        ; reg: 0x03d

label_077:                                                  ; address: 0x06ce

        movf    0x43, W                                     ; reg: 0x043
        andlw   0x0f
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_079
        movf    0x3e, W                                     ; reg: 0x03e
        sublw   0x01
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_079
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_078
        movf    0x3d, W                                     ; reg: 0x03d
        sublw   0x67
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_079

label_078:                                                  ; address: 0x06dd

        movlw   0x01
        movwf   0x3e                                        ; reg: 0x03e
        movlw   0x68
        movwf   0x3d                                        ; reg: 0x03d

label_079:                                                  ; address: 0x06e1

        movf    0x3e, W                                     ; reg: 0x03e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3d, W                                     ; reg: 0x03d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6

label_080:                                                  ; address: 0x06ea

        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    label_080
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x51, W                                     ; reg: 0x051
        movwf   (Common_RAM + 2)                            ; reg: 0x072
        movf    0x50, W                                     ; reg: 0x050
        movwf   (Common_RAM + 1)                            ; reg: 0x071
        movlw   0xc0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        iorwf   INTCON, F                                   ; reg: 0x00b
        retlw   0x00

function_028:                                               ; address: 0x06f6

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x44                                        ; reg: 0x044
        clrf    0x43                                        ; reg: 0x043
        clrf    0x4f                                        ; reg: 0x04f
        movlw   0x02
        movwf   0x4e                                        ; reg: 0x04e

label_081:                                                  ; address: 0x06fc

        movf    0x4f, W                                     ; reg: 0x04f
        sublw   0x00
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_082
        movf    0x4e, W                                     ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, RD                                  ; reg: 0x18c, bit: 0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    EEDATA, W                                   ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        addwf   0x43, F                                     ; reg: 0x0c3
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    0x44, F                                     ; reg: 0x0c4
        clrf    0x50                                        ; reg: 0x0d0
        btfsc   0x44, 0x7                                   ; reg: 0x0c4
        incf    0x50, F                                     ; reg: 0x0d0
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x43, F                                     ; reg: 0x0c3
        rlf     0x44, F                                     ; reg: 0x0c4
        movf    0x50, W                                     ; reg: 0x0d0
        addwf   0x43, F                                     ; reg: 0x0c3
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    0x44, F                                     ; reg: 0x0c4
        incf    0x4e, F                                     ; reg: 0x0ce
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        incf    0x4f, F                                     ; reg: 0x0cf
        goto    label_081

label_082:                                                  ; address: 0x071c

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_029:                                               ; address: 0x071e

        bsf     (Common_RAM + 14), 0x0                      ; reg: 0x07e
        bsf     (Common_RAM + 14), 0x1                      ; reg: 0x07e
        bsf     (Common_RAM + 14), 0x2                      ; reg: 0x07e
        bsf     (Common_RAM + 14), 0x3                      ; reg: 0x07e
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        clrf    PIR2                                        ; reg: 0x00d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, RD                                  ; reg: 0x18c, bit: 0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    EEDATA, W                                   ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        subwf   0x44, W                                     ; reg: 0x0c4
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_083
        bcf     (Common_RAM + 14), 0x0                      ; reg: 0x07e
        bcf     (Common_RAM + 14), 0x1                      ; reg: 0x07e

label_083:                                                  ; address: 0x0730

        movlw   0x01
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, RD                                  ; reg: 0x18c, bit: 0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    EEDATA, W                                   ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        subwf   0x43, W                                     ; reg: 0x0c3
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_084
        bcf     (Common_RAM + 14), 0x0                      ; reg: 0x07e
        bcf     (Common_RAM + 14), 0x2                      ; reg: 0x07e

label_084:                                                  ; address: 0x0740

        movlw   0x02
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, RD                                  ; reg: 0x18c, bit: 0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    EEDATA, W                                   ; reg: 0x10c
        sublw   0x07
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_085
        bcf     (Common_RAM + 14), 0x0                      ; reg: 0x07e
        bcf     (Common_RAM + 14), 0x3                      ; reg: 0x07e

label_085:                                                  ; address: 0x074e

        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        retlw   0x00

function_030:                                               ; address: 0x0750

        call    function_028
        call    function_029
        retlw   0x00

function_031:                                               ; address: 0x0753

        call    function_030
        movf    (Common_RAM + 14), W                        ; reg: 0x07e
        andlw   0x0f
        sublw   0x0f
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_086
        call    function_030
        movf    (Common_RAM + 14), W                        ; reg: 0x07e
        andlw   0x0f
        sublw   0x0f
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_086

label_086:                                                  ; address: 0x075f

        retlw   0x00

function_032:                                               ; address: 0x0760

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x54, W                                     ; reg: 0x054
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6d, W                                     ; reg: 0x06d
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_087
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x54, W                                     ; reg: 0x054
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x6d                                        ; reg: 0x06d

label_087:                                                  ; address: 0x076a

        retlw   0x00

function_033:                                               ; address: 0x076b

        bcf     0x56, 0x7                                   ; reg: 0x056
        call    function_008
        retlw   0x00

function_034:                                               ; address: 0x076e

        bsf     0x56, 0x7                                   ; reg: 0x056
        call    function_008
        retlw   0x00

function_035:                                               ; address: 0x0771

        movlw   0x54

label_088:                                                  ; address: 0x0772

        btfss   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    label_088
        movwf   TXREG                                       ; reg: 0x019
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x56                                        ; reg: 0x056
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_013
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x56                                        ; reg: 0x056
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_013
        movlw   0x0a

label_089:                                                  ; address: 0x0780

        btfss   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    label_089
        movwf   TXREG                                       ; reg: 0x019
        retlw   0x00
        movf    0x48, W                                     ; reg: 0x048
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x48                                        ; reg: 0x048
        clrf    (Common_RAM + 3)                            ; reg: 0x073
        bcf     0x49, 0x7                                   ; reg: 0x049
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x2f
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_090
        btfss   0x50, 0x5                                   ; reg: 0x050
        goto    label_092

label_090:                                                  ; address: 0x0792

        movf    0x5d, W                                     ; reg: 0x05d
        andlw   0x07
        movwf   (Common_RAM + 4)                            ; reg: 0x074
        incf    (Common_RAM + 4), F                         ; reg: 0x074

label_091:                                                  ; address: 0x0796

        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x48, F                                     ; reg: 0x048
        incf    0x48, F                                     ; reg: 0x048
        decfsz  (Common_RAM + 4), F                         ; reg: 0x074
        goto    label_091

label_092:                                                  ; address: 0x079b

        movf    0x4f, F                                     ; reg: 0x04f
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_093
        bsf     0x49, 0x7                                   ; reg: 0x049
        movf    0x4f, W                                     ; reg: 0x04f
        iorwf   (Common_RAM + 3), F                         ; reg: 0x073

label_093:                                                  ; address: 0x07a1

        btfsc   0x2d, 0x0                                   ; reg: 0x02d
        goto    label_094
        movlw   0x41
        iorwf   (Common_RAM + 3), F                         ; reg: 0x073

label_094:                                                  ; address: 0x07a5

        btfsc   0x2d, 0x1                                   ; reg: 0x02d
        goto    label_095
        movlw   0x42
        iorwf   (Common_RAM + 3), F                         ; reg: 0x073

label_095:                                                  ; address: 0x07a9

        btfss   0x30, 0x0                                   ; reg: 0x030
        goto    label_096
        bsf     0x49, 0x7                                   ; reg: 0x049
        bsf     (Common_RAM + 3), 0x4                       ; reg: 0x073

label_096:                                                  ; address: 0x07ad

        btfss   0x50, 0x4                                   ; reg: 0x050
        goto    label_097
        bsf     0x49, 0x7                                   ; reg: 0x049
        movlw   0x06
        iorwf   (Common_RAM + 3), F                         ; reg: 0x073

label_097:                                                  ; address: 0x07b2

        movf    0x43, W                                     ; reg: 0x043
        andlw   0x0f
        sublw   0x01
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_098
        bsf     0x49, 0x7                                   ; reg: 0x049
        bsf     (Common_RAM + 3), 0x7                       ; reg: 0x073
        movlw   0x05
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_032

label_098:                                                  ; address: 0x07be

        movf    (Common_RAM + 3), W                         ; reg: 0x073
        iorwf   0x48, F                                     ; reg: 0x048
        btfss   0x49, 0x2                                   ; reg: 0x049
        goto    label_101
        btfsc   0x50, 0x1                                   ; reg: 0x050
        goto    label_099
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x60
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_101

label_099:                                                  ; address: 0x07c9

        btfss   0x56, 0x7                                   ; reg: 0x056
        goto    label_100
        call    function_033

label_100:                                                  ; address: 0x07cc

        goto    label_102

label_101:                                                  ; address: 0x07cd

        btfsc   0x56, 0x7                                   ; reg: 0x056
        goto    label_102
        call    function_034

label_102:                                                  ; address: 0x07d0

        btfss   0x4c, 0x3                                   ; reg: 0x04c
        goto    label_103
        movf    0x48, W                                     ; reg: 0x048
        iorwf   (Common_RAM + 3), F                         ; reg: 0x073
        bcf     0x49, 0x7                                   ; reg: 0x049

label_103:                                                  ; address: 0x07d5

        btfss   0x49, 0x4                                   ; reg: 0x049
        goto    label_104
        movf    (Common_RAM + 3), W                         ; reg: 0x073
        xorwf   0x48, F                                     ; reg: 0x048

label_104:                                                  ; address: 0x07d9

        call    function_006
        movf    0x48, W                                     ; reg: 0x048
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x53, W                                     ; reg: 0x053
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_105
        movf    0x42, F                                     ; reg: 0x042
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_105
        movlw   0x20
        movwf   0x54                                        ; reg: 0x054
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_035
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_105:                                                  ; address: 0x07eb

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_114
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x3f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_137
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x5f
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_137
        movlw   0x07
        movwf   0x2d                                        ; reg: 0x02d
        retlw   0x00

        ; code

        org     0x0800

function_036:                                               ; address: 0x0800

        btfss   PIR1, CCP1IF                                ; reg: 0x00c, bit: 2
        goto    label_113
        bcf     PIR1, CCP1IF                                ; reg: 0x00c, bit: 2
        movlw   0x01
        btfsc   0x49, 0x7                                   ; reg: 0x049
        movlw   0x04
        addwf   0x49, F                                     ; reg: 0x049
        bcf     0x49, 0x5                                   ; reg: 0x049
        incf    0x3b, F                                     ; reg: 0x03b
        incfsz  0x3c, W                                     ; reg: 0x03c
        movwf   0x3c                                        ; reg: 0x03c
        movlw   0xf0
        btfss   PORTE, RE1                                  ; reg: 0x009, bit: 1
        btfss   PORTB, RB1                                  ; reg: 0x006, bit: 1
        andwf   0x3b, F                                     ; reg: 0x03b
        movf    0x54, W                                     ; reg: 0x054
        sublw   0x07
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_106
        incf    0x55, F                                     ; reg: 0x055
        bsf     0x5d, 0x7                                   ; reg: 0x05d

label_106:                                                  ; address: 0x0815

        btfss   RCSTA, OERR                                 ; reg: 0x018, bit: 1
        goto    label_107
        bcf     RCSTA, OERR                                 ; reg: 0x018, bit: 1
        bcf     RCSTA, CREN                                 ; reg: 0x018, bit: 4
        bsf     RCSTA, CREN                                 ; reg: 0x018, bit: 4

label_107:                                                  ; address: 0x081a

        movf    0x4e, F                                     ; reg: 0x04e
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_108
        decf    0x4e, F                                     ; reg: 0x04e
        bsf     0x4c, 0x3                                   ; reg: 0x04c
        goto    label_109

label_108:                                                  ; address: 0x0820

        bcf     0x4c, 0x3                                   ; reg: 0x04c

label_109:                                                  ; address: 0x0821

        btfss   0x4a, 0x0                                   ; reg: 0x04a
        goto    label_110
        incf    0x5f, F                                     ; reg: 0x05f

label_110:                                                  ; address: 0x0824

        btfss   0x4a, 0x0                                   ; reg: 0x04a
        goto    label_111
        btfss   0x4a, 0x1                                   ; reg: 0x04a
        goto    label_111
        btfss   0x4a, 0x2                                   ; reg: 0x04a
        goto    label_111
        btfss   0x4a, 0x3                                   ; reg: 0x04a
        goto    label_111
        btfss   0x4a, 0x4                                   ; reg: 0x04a
        goto    label_111
        incf    0x5e, F                                     ; reg: 0x05e
        incf    0x60, F                                     ; reg: 0x060
        movf    0x6d, F                                     ; reg: 0x06d
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_111
        decf    0x6d, F                                     ; reg: 0x06d

label_111:                                                  ; address: 0x0834

        incf    Common_RAM, F                               ; reg: 0x070
        btfsc   0x51, 0x4                                   ; reg: 0x051
        goto    label_112
        incfsz  0x4a, F                                     ; reg: 0x04a
        goto    label_112
        incfsz  0x4b, W                                     ; reg: 0x04b
        movwf   0x4b                                        ; reg: 0x04b

label_112:                                                  ; address: 0x083b

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_015
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        btfss   PORTB, RB1                                  ; reg: 0x006, bit: 1
        goto    0x0047
        btfsc   PORTD, RD0                                  ; reg: 0x008, bit: 0
        goto    0x0046
        btfss   0x43, 0x4                                   ; reg: 0x043
        goto    0x0045
        bsf     0x43, 0x7                                   ; reg: 0x043
        goto    0x0047
        bsf     0x43, 0x4                                   ; reg: 0x043
        movf    0x33, F                                     ; reg: 0x033
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x004e
        bcf     PORTB, RB3                                  ; reg: 0x006, bit: 3
        clrf    0x37                                        ; reg: 0x037
        clrf    0x38                                        ; reg: 0x038
        goto    0x00b2
        btfsc   0x35, 0x7                                   ; reg: 0x035
        goto    0x0051
        goto    0x00b2
        bcf     0x35, 0x7                                   ; reg: 0x035
        movf    0x3c, W                                     ; reg: 0x03c
        sublw   0x09
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0058
        incf    0x3c, F                                     ; reg: 0x03c
        goto    0x00b2
        clrf    0x3c                                        ; reg: 0x03c
        movf    0x34, W                                     ; reg: 0x034
        sublw   0x04
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0069
        btfss   0x3b, 0x6                                   ; reg: 0x03b
        goto    0x0062
        bsf     0x4f, 0x5                                   ; reg: 0x04f

function_037:                                               ; address: 0x0860

        bsf     0x30, 0x7                                   ; reg: 0x030
        goto    0x0064
        movlw   0x10
        addwf   0x3b, F                                     ; reg: 0x03b
        movlw   0xff
        movwf   0x3c                                        ; reg: 0x03c
        movlw   0x02
        movwf   0x37                                        ; reg: 0x037
        goto    0x00b2
        movlw   0x0f
        andwf   0x3b, F                                     ; reg: 0x03b
        incfsz  0x33, W                                     ; reg: 0x033
        goto    0x0070
        movlw   0x01
        movwf   0x37                                        ; reg: 0x037
        goto    0x00b2
        movf    0x33, W                                     ; reg: 0x033
        subwf   0x34, W                                     ; reg: 0x034
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0075
        goto    0x00b2
        movf    0x33, W                                     ; reg: 0x033
        subwf   0x34, W                                     ; reg: 0x034
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0090
        movf    0x37, F                                     ; reg: 0x037
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x007d
        decf    0x37, F                                     ; reg: 0x037
        movf    0x34, W                                     ; reg: 0x034
        subwf   0x36, W                                     ; reg: 0x036
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x008b
        movf    0x34, W                                     ; reg: 0x034
        subwf   0x36, W                                     ; reg: 0x036
        sublw   0x0a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x008a
        movf    0x37, F                                     ; reg: 0x037
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x008a
        decf    0x37, F                                     ; reg: 0x037
        goto    0x008f
        incfsz  0x37, W                                     ; reg: 0x037
        goto    0x008e
        goto    0x008f
        incf    0x37, F                                     ; reg: 0x037
        goto    0x00aa
        movf    0x34, W                                     ; reg: 0x034
        subwf   0x33, W                                     ; reg: 0x033
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x00aa
        incfsz  0x37, W                                     ; reg: 0x037
        goto    0x0097
        goto    0x0098
        incf    0x37, F                                     ; reg: 0x037
        movf    0x36, W                                     ; reg: 0x036
        subwf   0x34, W                                     ; reg: 0x034
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x00a6
        movf    0x36, W                                     ; reg: 0x036
        subwf   0x34, W                                     ; reg: 0x034
        sublw   0x0a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x00a5
        incfsz  0x37, W                                     ; reg: 0x037
        goto    0x00a4
        goto    0x00a5
        incf    0x37, F                                     ; reg: 0x037
        goto    0x00aa
        movf    0x37, F                                     ; reg: 0x037
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x00aa
        decf    0x37, F                                     ; reg: 0x037
        movf    0x34, W                                     ; reg: 0x034
        movwf   0x36                                        ; reg: 0x036
        movf    0x37, F                                     ; reg: 0x037
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x00b2
        movlw   0x01
        movwf   0x37                                        ; reg: 0x037
        goto    0x00b2
        btfss   PORTB, RB4                                  ; reg: 0x006, bit: 4
        goto    0x00b6
        movlw   0x0c
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x57, W                                     ; reg: 0x057
        sublw   0xfc
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x00bb
        bsf     0x50, 0x0                                   ; reg: 0x050
        btfss   0x50, 0x0                                   ; reg: 0x050
        goto    0x00c4
        movf    0x57, W                                     ; reg: 0x057
        sublw   0xf4
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x00c3
        bcf     0x50, 0x0                                   ; reg: 0x050
        goto    0x00c4
        bsf     0x4c, 0x3                                   ; reg: 0x04c

label_113:                                                  ; address: 0x08c4

        btfsc   0x51, 0x3                                   ; reg: 0x051
        goto    0x00c9
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x0784

label_114:                                                  ; address: 0x08c8

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        retlw   0x00

function_038:                                               ; address: 0x08ca

        btfss   (Common_RAM + 14), 0x0                      ; reg: 0x07e
        goto    0x00e1
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x56, W                                     ; reg: 0x056
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x57                                        ; reg: 0x057
        movf    0x57, W                                     ; reg: 0x057
        sublw   0x64
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x00dc
        movlw   0x64
        movwf   0x57                                        ; reg: 0x057
        movf    0x57, W                                     ; reg: 0x057
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    0x00e5
        goto    0x00e5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movlw   0x64
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x00e5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_039:                                               ; address: 0x08e7

        movlw   0x20
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x64                                        ; reg: 0x064
        clrf    0x60                                        ; reg: 0x060
        clrf    0x61                                        ; reg: 0x061
        clrf    0x62                                        ; reg: 0x062
        clrf    0x63                                        ; reg: 0x063
        movf    0x5b, W                                     ; reg: 0x05b
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    0x5a, W                                     ; reg: 0x05a
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        movf    0x59, W                                     ; reg: 0x059
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x58, W                                     ; reg: 0x058
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        btfss   (Common_RAM + 7), 0x0                       ; reg: 0x077
        goto    0x0107
        movf    0x5c, W                                     ; reg: 0x05c
        addwf   0x60, F                                     ; reg: 0x060
        movf    0x5d, W                                     ; reg: 0x05d
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x5d, W                                     ; reg: 0x05d
        addwf   0x61, F                                     ; reg: 0x061
        movf    0x5e, W                                     ; reg: 0x05e
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x5e, W                                     ; reg: 0x05e
        addwf   0x62, F                                     ; reg: 0x062
        movf    0x5f, W                                     ; reg: 0x05f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x5f, W                                     ; reg: 0x05f
        addwf   0x63, F                                     ; reg: 0x063
        rrf     0x63, F                                     ; reg: 0x063
        rrf     0x62, F                                     ; reg: 0x062
        rrf     0x61, F                                     ; reg: 0x061
        rrf     0x60, F                                     ; reg: 0x060
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        rrf     (Common_RAM + 8), F                         ; reg: 0x078
        rrf     (Common_RAM + 7), F                         ; reg: 0x077
        decfsz  0x64, F                                     ; reg: 0x064
        goto    0x00f6
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_040:                                               ; address: 0x0913

        movlw   0x64
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x56                                        ; reg: 0x056
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x00ca
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x55                                        ; reg: 0x055
        clrf    0x57                                        ; reg: 0x057
        movlw   0xa0
        movwf   0x56                                        ; reg: 0x056
        clrf    0x59                                        ; reg: 0x059
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x58                                        ; reg: 0x058
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03b9
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x54                                        ; reg: 0x054
        clrf    0x53                                        ; reg: 0x053
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x52                                        ; reg: 0x052
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x51                                        ; reg: 0x051
        movlw   0x6e
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        btfss   (Common_RAM + 8), 0x0                       ; reg: 0x078
        goto    0x01ca
        movf    0x2f, W                                     ; reg: 0x02f
        sublw   0x7f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0162
        movlw   0x80
        subwf   0x2f, W                                     ; reg: 0x02f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x56                                        ; reg: 0x056
        clrf    0x5b                                        ; reg: 0x05b
        movf    0x56, W                                     ; reg: 0x056
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0x78
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        sublw   0x80
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x55                                        ; reg: 0x055
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x57                                        ; reg: 0x057
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x56                                        ; reg: 0x056
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x54                                        ; reg: 0x054
        clrf    0x53                                        ; reg: 0x053
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x52                                        ; reg: 0x052
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x51                                        ; reg: 0x051
        goto    0x019d
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x5b                                        ; reg: 0x05b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x2f, W                                     ; reg: 0x02f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0x30
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        sublw   0x40
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x55                                        ; reg: 0x055
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x5a                                        ; reg: 0x05a
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x59                                        ; reg: 0x059
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x58                                        ; reg: 0x058
        clrf    0x5f                                        ; reg: 0x05f
        clrf    0x5e                                        ; reg: 0x05e
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x00e7
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x53                                        ; reg: 0x053
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x52                                        ; reg: 0x052
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        movwf   0x51                                        ; reg: 0x051
        rrf     0x54, F                                     ; reg: 0x054
        rrf     0x53, F                                     ; reg: 0x053
        rrf     0x52, F                                     ; reg: 0x052
        rrf     0x51, F                                     ; reg: 0x051
        rrf     0x54, F                                     ; reg: 0x054
        rrf     0x53, F                                     ; reg: 0x053
        rrf     0x52, F                                     ; reg: 0x052
        rrf     0x51, F                                     ; reg: 0x051
        rrf     0x54, F                                     ; reg: 0x054
        rrf     0x53, F                                     ; reg: 0x053
        rrf     0x52, F                                     ; reg: 0x052
        rrf     0x51, F                                     ; reg: 0x051
        rrf     0x54, F                                     ; reg: 0x054
        rrf     0x53, F                                     ; reg: 0x053
        rrf     0x52, F                                     ; reg: 0x052
        rrf     0x51, F                                     ; reg: 0x051
        movlw   0x0f
        andwf   0x54, F                                     ; reg: 0x054
        movf    0x54, F                                     ; reg: 0x054
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x01ae
        movf    0x53, F                                     ; reg: 0x053
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x01ae
        movf    0x52, W                                     ; reg: 0x052
        sublw   0xf9
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x01b3
        xorlw   0xff
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x01ae
        movf    0x51, W                                     ; reg: 0x051
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x01b3
        clrf    0x54                                        ; reg: 0x054
        clrf    0x53                                        ; reg: 0x053
        movlw   0xfa
        movwf   0x52                                        ; reg: 0x052
        clrf    0x51                                        ; reg: 0x051
        movf    0x54, F                                     ; reg: 0x054
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x01c9
        movf    0x53, F                                     ; reg: 0x053
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x01c9
        movf    0x52, W                                     ; reg: 0x052
        sublw   0x03
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x01c9
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x01c3
        movf    0x51, W                                     ; reg: 0x051
        sublw   0xe7
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x01c9
        clrf    0x54                                        ; reg: 0x054
        clrf    0x53                                        ; reg: 0x053
        movlw   0x03
        movwf   0x52                                        ; reg: 0x052
        movlw   0xe8
        movwf   0x51                                        ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x51, W                                     ; reg: 0x051
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x52, W                                     ; reg: 0x052
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x4e                                        ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x4c, 0x4                                   ; reg: 0x04c
        goto    0x01e1
        movf    (Common_RAM + 6), W                         ; reg: 0x076
        subwf   (Common_RAM + 5), W                         ; reg: 0x075
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x01e1
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    0x4e, F                                     ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        rlf     0x4d, W                                     ; reg: 0x04d
        addlw   0x12
        movwf   0x51                                        ; reg: 0x051
        movf    0x4e, W                                     ; reg: 0x04e
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0045
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x52                                        ; reg: 0x052
        movf    0x4d, W                                     ; reg: 0x04d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0045
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x52, W                                     ; reg: 0x052
        addwf   0x51, W                                     ; reg: 0x051
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4d, W                                     ; reg: 0x04d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0045
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        subwf   0x6b, W                                     ; reg: 0x06b
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        swapf   (Common_RAM + 7), F                         ; reg: 0x077
        movlw   0x0f
        andwf   (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x4c, F                                     ; reg: 0x04c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0113
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x52                                        ; reg: 0x052
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x51                                        ; reg: 0x051
        rrf     0x52, W                                     ; reg: 0x052
        movwf   0x50                                        ; reg: 0x050
        rrf     0x51, W                                     ; reg: 0x051
        movwf   0x4f                                        ; reg: 0x04f
        rrf     0x50, F                                     ; reg: 0x050
        rrf     0x4f, F                                     ; reg: 0x04f
        rrf     0x50, F                                     ; reg: 0x050
        rrf     0x4f, F                                     ; reg: 0x04f
        movlw   0x1f
        andwf   0x50, F                                     ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3a, W                                     ; reg: 0x03a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x50, W                                     ; reg: 0x050
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x024e
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0226
        movf    0x4f, W                                     ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x39, W                                     ; reg: 0x039
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0225
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x024e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        rrf     0x50, F                                     ; reg: 0x050
        rrf     0x4f, F                                     ; reg: 0x04f
        rrf     0x50, F                                     ; reg: 0x050
        rrf     0x4f, F                                     ; reg: 0x04f
        rrf     0x50, F                                     ; reg: 0x050
        rrf     0x4f, F                                     ; reg: 0x04f
        movlw   0x1f
        andwf   0x50, F                                     ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3a, W                                     ; reg: 0x03a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x55                                        ; reg: 0x055
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x39, W                                     ; reg: 0x039
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x57                                        ; reg: 0x057
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x56                                        ; reg: 0x056
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04a2
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        sublw   0x0a
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 9), W                         ; reg: 0x079
        goto    0x0249
        movlw   0x00
        goto    0x024a
        sublw   0x00
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x4c, F                                     ; reg: 0x04c
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4e, W                                     ; reg: 0x04e
        clrf    (Common_RAM + 8)                            ; reg: 0x078
        subwf   0x4d, W                                     ; reg: 0x04d
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x025b
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        goto    0x0267
        clrf    (Common_RAM + 7)                            ; reg: 0x077
        movlw   0x08
        movwf   0x4f                                        ; reg: 0x04f
        rlf     0x4d, F                                     ; reg: 0x04d
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        movf    0x4e, W                                     ; reg: 0x04e
        subwf   (Common_RAM + 7), W                         ; reg: 0x077
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        rlf     (Common_RAM + 8), F                         ; reg: 0x078
        decfsz  0x4f, F                                     ; reg: 0x04f
        goto    0x025e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_128
        movf    0x6d, F                                     ; reg: 0x06d
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_115
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x60
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_117

label_115:                                                  ; address: 0x0a73

        btfsc   (Common_RAM + 14), 0x6                      ; reg: 0x07e
        goto    label_117
        clrf    (Common_RAM + 4)                            ; reg: 0x074

label_116:                                                  ; address: 0x0a76

        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_117
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    0x57, W                                     ; reg: 0x057
        movwf   INDF                                        ; reg: 0x000
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x6b                                        ; reg: 0x06b
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        goto    label_116

label_117:                                                  ; address: 0x0a83

        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x3f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_129
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x5f
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_129
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x5a, W                                     ; reg: 0x05a
        subwf   0x57, W                                     ; reg: 0x057
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_118
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x5a                                        ; reg: 0x05a

label_118:                                                  ; address: 0x0a96

        movf    0x61, W                                     ; reg: 0x061
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_127
        movf    0x5a, W                                     ; reg: 0x05a
        subwf   0x6b, W                                     ; reg: 0x06b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_120
        incf    0x6b, F                                     ; reg: 0x06b
        movf    0x5a, W                                     ; reg: 0x05a
        sublw   0xc7
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_119
        movf    0x5a, W                                     ; reg: 0x05a
        subwf   0x6b, W                                     ; reg: 0x06b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_119
        incf    0x6b, F                                     ; reg: 0x06b
        movf    0x5a, W                                     ; reg: 0x05a
        sublw   0x95
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_119
        movf    0x5a, W                                     ; reg: 0x05a
        subwf   0x6b, W                                     ; reg: 0x06b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_119
        incf    0x6b, F                                     ; reg: 0x06b

label_119:                                                  ; address: 0x0ab1

        movf    0x6b, W                                     ; reg: 0x06b
        movwf   0x5a                                        ; reg: 0x05a

label_120:                                                  ; address: 0x0ab3

        movlw   0x63
        addwf   0x62, W                                     ; reg: 0x062
        movwf   FSR                                         ; reg: 0x004
        movf    0x5a, W                                     ; reg: 0x05a
        movwf   INDF                                        ; reg: 0x000
        btfsc   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    label_126
        clrf    0x6b                                        ; reg: 0x06b
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_125
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        subwf   0x5a, W                                     ; reg: 0x05a
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_121
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_121
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    0x5a, W                                     ; reg: 0x05a
        movwf   INDF                                        ; reg: 0x000

label_121:                                                  ; address: 0x0ace

        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6b, W                                     ; reg: 0x06b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_122
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x6b                                        ; reg: 0x06b

label_122:                                                  ; address: 0x0add

        btfss   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    label_123
        movlw   0x10
        goto    label_124

label_123:                                                  ; address: 0x0ae1

        movlw   0x18

label_124:                                                  ; address: 0x0ae2

        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movwf   0x53                                        ; reg: 0x053
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_014
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        goto    0x02bc

label_125:                                                  ; address: 0x0aee

        movlw   0x06
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_126:                                                  ; address: 0x0af9

        btfss   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    0x02fd
        movlw   0x10
        goto    0x02fe
        movlw   0x18
        addwf   0x62, W                                     ; reg: 0x062
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x5a, W                                     ; reg: 0x05a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x05
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x62, W                                     ; reg: 0x062
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        incf    0x62, F                                     ; reg: 0x062
        movf    0x6b, W                                     ; reg: 0x06b
        subwf   0x5a, W                                     ; reg: 0x05a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0340
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0328
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    0x6b, W                                     ; reg: 0x06b
        movwf   INDF                                        ; reg: 0x000
        movf    0x6b, W                                     ; reg: 0x06b
        movwf   0x6c                                        ; reg: 0x06c
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        goto    0x031b
        movlw   0x18
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x06
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x61                                        ; reg: 0x061

label_127:                                                  ; address: 0x0b43

        call    0x01d1
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        btfsc   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    0x03ad
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x6e                                        ; reg: 0x06e
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x039a
        movf    0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x48, W                                     ; reg: 0x048
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0397
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        subwf   0x49, W                                     ; reg: 0x049
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0368
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0368
        movlw   0x10
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x6e, F                                     ; reg: 0x06e
        goto    0x0396
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x21, W                                     ; reg: 0x021
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0397
        movf    0x21, W                                     ; reg: 0x021
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        subwf   0x49, W                                     ; reg: 0x049
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x038d
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x038d
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    0x6e, F                                     ; reg: 0x06e
        movlw   0x10
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6e, W                                     ; reg: 0x06e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x0396
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movlw   0x10
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   0x49                                        ; reg: 0x049
        movwf   0x53                                        ; reg: 0x053
        clrf    0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x034c
        movlw   0x07
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6e, W                                     ; reg: 0x06e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x6e, W                                     ; reg: 0x06e
        sublw   0x2f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03ab
        bsf     (Common_RAM + 14), 0x7                      ; reg: 0x07e
        clrf    0x62                                        ; reg: 0x062
        goto    0x03fa
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x62, W                                     ; reg: 0x062
        sublw   0x07
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03e6
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03df
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074

function_041:                                               ; address: 0x0bb9

        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        rlf     0x48, W                                     ; reg: 0x048
        movwf   0x4a                                        ; reg: 0x04a
        rlf     0x4a, F                                     ; reg: 0x04a
        movlw   0xfc
        andwf   0x4a, F                                     ; reg: 0x04a
        movlw   0x09
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x4d                                        ; reg: 0x04d
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x4e                                        ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x0252

label_128:                                                  ; address: 0x0bcf

        movf    (Common_RAM + 8), W                         ; reg: 0x078

function_042:                                               ; address: 0x0bd0

        subwf   0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x49, W                                     ; reg: 0x049
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x03dc
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03dc
        bcf     (Common_RAM + 14), 0x7                      ; reg: 0x07e
        bcf     (Common_RAM + 14), 0x6                      ; reg: 0x07e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     0x30, 0x6                                   ; reg: 0x030
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x03b3
        btfss   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    0x03e5
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        bsf     (Common_RAM + 14), 0x6                      ; reg: 0x07e
        bcf     0x30, 0x6                                   ; reg: 0x030
        goto    0x03fa
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x48, W                                     ; reg: 0x048
        subwf   0x49, W                                     ; reg: 0x049
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x03fb
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03fb
        btfss   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    0x03fb
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        bsf     (Common_RAM + 14), 0x6                      ; reg: 0x07e
        bcf     0x30, 0x6                                   ; reg: 0x030
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_129:                                                  ; address: 0x0bfb

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x62, W                                     ; reg: 0x062
        sublw   0x07
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0401
        clrf    0x62                                        ; reg: 0x062
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_132
        btfss   (Common_RAM + 14), 0x0                      ; reg: 0x07e
        goto    label_130
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_017
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        goto    0x0415
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_130:                                                  ; address: 0x0c12

        movlw   0x10
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_133
        btfss   0x43, 0x5                                   ; reg: 0x043
        goto    label_131
        btfss   PORTB, RB1                                  ; reg: 0x006, bit: 1
        goto    label_131
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_027
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_131:                                                  ; address: 0x0c22

        btfss   PORTB, RB1                                  ; reg: 0x006, bit: 1
        goto    0x0455
        btfss   0x43, 0x7                                   ; reg: 0x043
        goto    0x0443
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x06a9
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0xf0
        andwf   0x43, F                                     ; reg: 0x043
        movf    0x47, W                                     ; reg: 0x047
        movwf   0x45                                        ; reg: 0x045
        movf    0x46, W                                     ; reg: 0x046
        movwf   0x44                                        ; reg: 0x044
        movf    0x45, W                                     ; reg: 0x045
        sublw   0x13
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x043e
        xorlw   0xff
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x043a
        movf    0x44, W                                     ; reg: 0x044
        sublw   0x50
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x043e
        movlw   0x14
        movwf   0x45                                        ; reg: 0x045
        movlw   0x50
        movwf   0x44                                        ; reg: 0x044
        clrf    0x47                                        ; reg: 0x047
        clrf    0x46                                        ; reg: 0x046
        bcf     0x43, 0x7                                   ; reg: 0x043
        bcf     0x43, 0x4                                   ; reg: 0x043
        goto    0x0454
        movf    (Common_RAM + 1), F                         ; reg: 0x071
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0454
        movf    (Common_RAM + 2), F                         ; reg: 0x072
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0454
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x06a9
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x43, W                                     ; reg: 0x043
        andlw   0x0f
        sublw   0x06
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0453
        incf    0x43, F                                     ; reg: 0x043
        goto    0x0454
        bsf     0x4f, 0x7                                   ; reg: 0x04f
        goto    0x04c0
        movf    (Common_RAM + 1), F                         ; reg: 0x071
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04c0
        movf    (Common_RAM + 2), F                         ; reg: 0x072
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04c0
        btfsc   0x4f, 0x3                                   ; reg: 0x04f
        goto    0x04c0
        btfsc   0x43, 0x5                                   ; reg: 0x043
        goto    0x04c0
        goto    0x026b

label_132:                                                  ; address: 0x0c60

        bsf     PORTB, RB1                                  ; reg: 0x006, bit: 1
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        addlw   0x50
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movwf   0x49                                        ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x0404

label_133:                                                  ; address: 0x0c69

        movf    (Common_RAM + 8), W                         ; reg: 0x078
        addwf   0x39, F                                     ; reg: 0x039
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    0x3a, F                                     ; reg: 0x03a
        call    0x0113
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x3a, W                                     ; reg: 0x03a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0482
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x047a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x39, W                                     ; reg: 0x039
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0482
        bsf     0x50, 0x1                                   ; reg: 0x050
        call    0x0113
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x39, F                                     ; reg: 0x039
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 9), W                         ; reg: 0x079
        subwf   0x3a, F                                     ; reg: 0x03a
        incf    0x61, F                                     ; reg: 0x061
        movf    0x45, F                                     ; reg: 0x045
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x048e
        movf    0x44, W                                     ; reg: 0x044
        sublw   0x63
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x048e
        movlw   0x02
        movwf   0x45                                        ; reg: 0x045
        movlw   0x8a
        movwf   0x44                                        ; reg: 0x044
        btfsc   0x43, 0x6                                   ; reg: 0x043
        goto    0x04ab
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x44, W                                     ; reg: 0x044
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        rlf     0x45, W                                     ; reg: 0x045
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x51                                        ; reg: 0x051
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x50                                        ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    0x049e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x51, W                                     ; reg: 0x051
        movwf   (Common_RAM + 2)                            ; reg: 0x072
        movf    0x50, W                                     ; reg: 0x050
        movwf   (Common_RAM + 1)                            ; reg: 0x071
        movlw   0xc0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        iorwf   INTCON, F                                   ; reg: 0x00b
        bcf     0x43, 0x6                                   ; reg: 0x043
        goto    0x04c0
        movf    0x45, W                                     ; reg: 0x045
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x44, W                                     ; reg: 0x044
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    0x04b4
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x51, W                                     ; reg: 0x051
        movwf   (Common_RAM + 2)                            ; reg: 0x072
        movf    0x50, W                                     ; reg: 0x050
        movwf   (Common_RAM + 1)                            ; reg: 0x071
        movlw   0xc0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        iorwf   INTCON, F                                   ; reg: 0x00b
        bcf     0x43, 0x6                                   ; reg: 0x043
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_238

function_043:                                               ; address: 0x0cc3

        movf    0x3b, W                                     ; reg: 0x03b
        andlw   0x0f
        sublw   0x0c
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_339
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        bcf     0x30, 0x0                                   ; reg: 0x030
        btfsc   PORTD, RD4                                  ; reg: 0x008, bit: 4
        bsf     0x30, 0x0                                   ; reg: 0x030
        btfsc   PORTD, RD4                                  ; reg: 0x008, bit: 4
        goto    label_341
        clrf    0x5e                                        ; reg: 0x05e
        goto    label_342
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_060
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x0c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0760
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x5e, W                                     ; reg: 0x05e
        sublw   0xe0
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04e1
        bsf     0x4f, 0x4                                   ; reg: 0x04f
        movlw   0xe1
        movwf   0x5e                                        ; reg: 0x05e
        btfss   PORTD, RD1                                  ; reg: 0x008, bit: 1
        goto    0x04ef
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x07ef
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     0x4f, 0x3                                   ; reg: 0x04f
        movlw   0x18
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0760
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x04f6
        movf    0x5f, W                                     ; reg: 0x05f
        sublw   0xb3
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04f6
        bcf     0x30, 0x2                                   ; reg: 0x030
        bcf     0x4f, 0x3                                   ; reg: 0x04f
        clrf    0x5f                                        ; reg: 0x05f
        movf    0x5f, W                                     ; reg: 0x05f
        sublw   0xb3
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04fe
        bsf     0x30, 0x2                                   ; reg: 0x030
        bsf     0x4f, 0x3                                   ; reg: 0x04f
        movlw   0xb4
        movwf   0x5f                                        ; reg: 0x05f
        btfss   0x4f, 0x6                                   ; reg: 0x04f
        goto    0x0501
        bsf     0x30, 0x3                                   ; reg: 0x030
        retlw   0x00
        btfss   (Common_RAM + 14), 0x0                      ; reg: 0x07e
        goto    0x052a
        movlw   0x68
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        incf    0x4c, F                                     ; reg: 0x04c
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        movf    0x4a, W                                     ; reg: 0x04a
        sublw   0x82
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0520
        movlw   0x82
        movwf   0x4a                                        ; reg: 0x04a
        movlw   0x28
        addwf   0x4a, W                                     ; reg: 0x04a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0528
        movlw   0x28
        addwf   0x4a, W                                     ; reg: 0x04a
        movwf   0x4b                                        ; reg: 0x04b
        goto    0x052f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movlw   0x5a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movlw   0xaa
        movwf   0x4b                                        ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   0x51, 0x3                                   ; reg: 0x051
        goto    0x05a3
        movf    0x57, W                                     ; reg: 0x057
        sublw   0x13
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0547
        clrf    0x29                                        ; reg: 0x029
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x20
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0546
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        movlw   0xfc
        andwf   (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        addlw   0x19
        movwf   0x29                                        ; reg: 0x029
        goto    0x05a3
        movf    0x57, W                                     ; reg: 0x057
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0551
        movlw   0x19
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x29                                        ; reg: 0x029
        goto    0x059d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x57, W                                     ; reg: 0x057
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0559
        movlw   0x64
        movwf   0x29                                        ; reg: 0x029
        goto    0x059d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4a, W                                     ; reg: 0x04a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x57, W                                     ; reg: 0x057
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x4e                                        ; reg: 0x04e
        clrf    0x57                                        ; reg: 0x057
        movlw   0x4b
        movwf   0x56                                        ; reg: 0x056
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x59                                        ; reg: 0x059
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x58                                        ; reg: 0x058
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03b9
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4f                                        ; reg: 0x04f
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   0x4b, W                                     ; reg: 0x04b
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        movwf   0x50                                        ; reg: 0x050
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x51                                        ; reg: 0x051
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x55                                        ; reg: 0x055
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x54                                        ; reg: 0x054
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x57                                        ; reg: 0x057
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x56                                        ; reg: 0x056
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04a2
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4f                                        ; reg: 0x04f
        movlw   0x19
        addwf   0x4f, W                                     ; reg: 0x04f
        movwf   0x48                                        ; reg: 0x048
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x49                                        ; reg: 0x049
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    0x49, F                                     ; reg: 0x049
        movf    0x49, F                                     ; reg: 0x049
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0597
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x64
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x059a
        clrf    0x49                                        ; reg: 0x049
        movlw   0x64
        movwf   0x48                                        ; reg: 0x048
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x29                                        ; reg: 0x029
        movf    0x29, W                                     ; reg: 0x029
        sublw   0x18
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x05a3
        movlw   0x19
        movwf   0x29                                        ; reg: 0x029
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_239

label_134:                                                  ; address: 0x0da6

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x20, W                                     ; reg: 0x020
        movwf   0x4a                                        ; reg: 0x04a
        bcf     0x4b, 0x0                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   0x51, 0x3                                   ; reg: 0x051
        goto    0x0724
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x20, F                                     ; reg: 0x020
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_345
        movf    0x22, W                                     ; reg: 0x022
        movwf   0x48                                        ; reg: 0x048
        clrf    0x49                                        ; reg: 0x049
        btfsc   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        incf    0x49, F                                     ; reg: 0x049
        decfsz  0x20, W                                     ; reg: 0x020
        goto    label_347
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x57, W                                     ; reg: 0x057
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        clrf    0x49                                        ; reg: 0x049
        btfsc   (Common_RAM + 14), 0x6                      ; reg: 0x07e
        incf    0x49, F                                     ; reg: 0x049
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x02
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_349
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x2e, W                                     ; reg: 0x02e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        clrf    0x49                                        ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x30, 0x6                                   ; reg: 0x030
        goto    label_348
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    0x49, F                                     ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x03
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_351
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x2f, W                                     ; reg: 0x02f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        clrf    0x49                                        ; reg: 0x049
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x04
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_353
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x34, W                                     ; reg: 0x034
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        clrf    0x49                                        ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x50, 0x0                                   ; reg: 0x050
        goto    label_352
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    0x49, F                                     ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x05
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_354
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x37, W                                     ; reg: 0x037
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x62, W                                     ; reg: 0x062
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x06
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_355
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x29, W                                     ; reg: 0x029
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x07
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_356
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x08
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_359
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x2d, W                                     ; reg: 0x02d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6c, W                                     ; reg: 0x06c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x09
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_360
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4c, W                                     ; reg: 0x04c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0a
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_362
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3a, W                                     ; reg: 0x03a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0b
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_364
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x39, W                                     ; reg: 0x039
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0c
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_368
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_062
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6d, W                                     ; reg: 0x06d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0d
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x064b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0113
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0e
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0654
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x45, W                                     ; reg: 0x045
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0f
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0660
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x44, W                                     ; reg: 0x044
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x60, W                                     ; reg: 0x060
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0668
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3e, W                                     ; reg: 0x03e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x11
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0670
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3d, W                                     ; reg: 0x03d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x12
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0676
        movf    (Common_RAM + 14), W                        ; reg: 0x07e
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x13
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x067e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4f, W                                     ; reg: 0x04f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x14
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0686
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x5d, W                                     ; reg: 0x05d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x15
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x068e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x58, W                                     ; reg: 0x058
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x16
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0696
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x5f, W                                     ; reg: 0x05f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x17
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x069e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x5e, W                                     ; reg: 0x05e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x18
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x06a7
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x33, W                                     ; reg: 0x033
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x19
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x06b1
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x01d1
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x1a
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x06b8
        movf    0x47, W                                     ; reg: 0x047
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x1b
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x06bf
        movf    0x46, W                                     ; reg: 0x046
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x1c
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x06c8
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x40, W                                     ; reg: 0x040
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x1d
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x06d1
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3f, W                                     ; reg: 0x03f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x1e
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0700
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x01d1
        rlf     (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        rlf     0x4d, F                                     ; reg: 0x04d
        movlw   0xfc
        andwf   0x4d, F                                     ; reg: 0x04d
        movlw   0x6b
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        clrf    0x5b                                        ; reg: 0x05b
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4f                                        ; reg: 0x04f
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4e                                        ; reg: 0x04e
        rrf     0x4f, W                                     ; reg: 0x04f
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        rrf     0x4e, W                                     ; reg: 0x04e
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x21                                        ; reg: 0x021
        movf    0x21, W                                     ; reg: 0x021
        movwf   0x48                                        ; reg: 0x048
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x0f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0709
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x17
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0709
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        btfsc   0x4b, 0x0                                   ; reg: 0x04b
        goto    0x0714
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x53                                        ; reg: 0x053
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x20, W                                     ; reg: 0x020
        movwf   0x54                                        ; reg: 0x054
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x55                                        ; reg: 0x055
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0771
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    0x20, F                                     ; reg: 0x020
        movf    0x20, W                                     ; reg: 0x020
        sublw   0x1e
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0723
        clrf    0x20                                        ; reg: 0x020
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_240

label_135:                                                  ; address: 0x0f27

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x40, W                                     ; reg: 0x040
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_242

function_044:                                               ; address: 0x0f2e

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x51                                        ; reg: 0x051
        movf    0x40, F                                     ; reg: 0x040
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0739
        incfsz  0x51, F                                     ; reg: 0x051
        goto    0x0738
        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    0x075e
        goto    0x0730
        movf    0x40, F                                     ; reg: 0x040
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x075b
        movf    0x40, W                                     ; reg: 0x040
        subwf   0x41, W                                     ; reg: 0x041
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0743
        movf    0x40, W                                     ; reg: 0x040
        subwf   0x41, W                                     ; reg: 0x041
        movwf   0x52                                        ; reg: 0x052
        movf    0x41, W                                     ; reg: 0x041
        subwf   0x40, W                                     ; reg: 0x040
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0747
        movf    0x40, W                                     ; reg: 0x040
        subwf   0x41, W                                     ; reg: 0x041
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x074f
        movf    0x40, W                                     ; reg: 0x040
        sublw   0x1d
        addwf   0x41, W                                     ; reg: 0x041
        movwf   0x52                                        ; reg: 0x052
        movf    0x52, W                                     ; reg: 0x052
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movlw   0xa3
        addwf   (Common_RAM + 8), W                         ; reg: 0x078
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        movwf   0x51                                        ; reg: 0x051
        decf    0x40, F                                     ; reg: 0x040
        movf    0x51, W                                     ; reg: 0x051
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    0x075e
        goto    0x075e
        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    0x075e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x51, W                                     ; reg: 0x051
        sublw   0x2f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x076c
        movf    0x51, W                                     ; reg: 0x051
        sublw   0x39
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x076c
        movlw   0x30
        subwf   0x51, W                                     ; reg: 0x051
        movwf   0x52                                        ; reg: 0x052
        movf    0x51, W                                     ; reg: 0x051
        sublw   0x40
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0778
        movf    0x51, W                                     ; reg: 0x051
        sublw   0x46
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0778
        movlw   0x41
        subwf   0x51, W                                     ; reg: 0x051
        addlw   0x0a
        movwf   0x52                                        ; reg: 0x052
        movf    0x52, W                                     ; reg: 0x052
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_045:                                               ; address: 0x0f7c

        call    0x072e
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4f                                        ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x072e
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x51                                        ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0760
        swapf   (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        movlw   0xf0
        andwf   0x4e, F                                     ; reg: 0x04e
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x51                                        ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0760
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x4e, F                                     ; reg: 0x04e
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_046:                                               ; address: 0x0f99

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x50, W                                     ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x4a, W                                     ; reg: 0x04a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x52                                        ; reg: 0x052
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    0x52, F                                     ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x52, W                                     ; reg: 0x052
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07b9
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x07b5
        movf    0x51, W                                     ; reg: 0x051
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07b4
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x07b9
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0000
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x07a5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_047:                                               ; address: 0x0fbb

        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    0x07bc
        movlw   0x1f
        andwf   PORTD, F                                    ; reg: 0x008
        movlw   0x80
        addwf   PORTD, F                                    ; reg: 0x008
        bcf     0x51, 0x0                                   ; reg: 0x051
        btfsc   PORTD, RD3                                  ; reg: 0x008, bit: 3
        bsf     0x51, 0x0                                   ; reg: 0x051
        movlw   0x20
        addwf   PORTD, F                                    ; reg: 0x008
        bcf     0x51, 0x1                                   ; reg: 0x051
        btfsc   PORTD, RD3                                  ; reg: 0x008, bit: 3
        bsf     0x51, 0x1                                   ; reg: 0x051
        movlw   0x20
        addwf   PORTD, F                                    ; reg: 0x008
        bcf     0x51, 0x2                                   ; reg: 0x051
        btfsc   PORTD, RD3                                  ; reg: 0x008, bit: 3
        bsf     0x51, 0x2                                   ; reg: 0x051
        movlw   0xc0
        iorwf   INTCON, F                                   ; reg: 0x00b
        retlw   0x00

function_048:                                               ; address: 0x0fd3

        movf    0x6f, W                                     ; reg: 0x06f
        sublw   0x05
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07de
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x028d
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     0x56, 0x5                                   ; reg: 0x056
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x01dc
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        retlw   0x00

function_049:                                               ; address: 0x0fdf

        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x026d
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x027d
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        btfsc   PORTC, RC0                                  ; reg: 0x007, bit: 0
        goto    0x07f3
        btfsc   PORTC, RC1                                  ; reg: 0x007, bit: 1
        goto    0x07f3
        bcf     0x2d, 0x7                                   ; reg: 0x02d
        goto    0x07f4
        bsf     0x2d, 0x7                                   ; reg: 0x02d
        retlw   0x00

label_136:                                                  ; address: 0x0ff5

        clrf    0x4d                                        ; reg: 0x04d
        bsf     0x5d, 0x6                                   ; reg: 0x05d
        bcf     0x5d, 0x3                                   ; reg: 0x05d
        bcf     0x5d, 0x5                                   ; reg: 0x05d
        bcf     0x5d, 0x7                                   ; reg: 0x05d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a

label_137:                                                  ; address: 0x0ffb

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_195

        ; code

        org     0x1000

function_050:                                               ; address: 0x1000

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_027
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x06
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_046
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     0x5d, 0x5                                   ; reg: 0x05d
        bcf     0x5d, 0x7                                   ; reg: 0x05d
        btfss   0x4f, 0x6                                   ; reg: 0x04f
        goto    label_138
        movlw   0x00
        goto    label_139

label_138:                                                  ; address: 0x1012

        movlw   0x5a

label_139:                                                  ; address: 0x1013

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     0x50, 0x3                                   ; reg: 0x050

label_140:                                                  ; address: 0x1017

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4e, F                                     ; reg: 0x04e
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_152
        clrf    0x40                                        ; reg: 0x040
        clrf    0x41                                        ; reg: 0x041
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_043
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x3c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4f                                        ; reg: 0x04f

label_141:                                                  ; address: 0x1026

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   PORTD, RD1                                  ; reg: 0x008, bit: 1
        goto    label_143
        btfsc   0x4f, 0x3                                   ; reg: 0x04f
        goto    label_142
        btfss   0x30, 0x0                                   ; reg: 0x030
        goto    label_145

label_142:                                                  ; address: 0x102d

        btfsc   (Common_RAM + 14), 0x6                      ; reg: 0x07e
        goto    label_145

label_143:                                                  ; address: 0x102f

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4f, F                                     ; reg: 0x04f
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_144
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_145

label_144:                                                  ; address: 0x1035

        clrf    0x40                                        ; reg: 0x040
        clrf    0x41                                        ; reg: 0x041
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PORTB, RB5                                  ; reg: 0x006, bit: 5
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_043
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_046
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        decf    0x4f, F                                     ; reg: 0x04f
        goto    label_141
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_145:                                                  ; address: 0x104b

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4f, F                                     ; reg: 0x04f
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_146
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x30, 0x3                                   ; reg: 0x030
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_152
        goto    label_147

label_146:                                                  ; address: 0x1054

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PORTB, RB5                                  ; reg: 0x006, bit: 5
        bcf     0x4f, 0x6                                   ; reg: 0x04f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_147:                                                  ; address: 0x1058

        movlw   0x01
        movwf   0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_046
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_047
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x00
        btfss   0x51, 0x0                                   ; reg: 0x051
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        movlw   0x00
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   0x50, 0x3                                   ; reg: 0x050
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        xorwf   0x50, W                                     ; reg: 0x050
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_148
        decf    0x4e, F                                     ; reg: 0x04e
        goto    label_150

label_148:                                                  ; address: 0x1074

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   0x50, 0x3                                   ; reg: 0x050
        goto    label_149
        bsf     0x50, 0x3                                   ; reg: 0x050
        goto    label_151

label_149:                                                  ; address: 0x1079

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_152

label_150:                                                  ; address: 0x107b

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_151:                                                  ; address: 0x107c

        goto    label_140
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_152:                                                  ; address: 0x107e

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PORTB, RB5                                  ; reg: 0x006, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4e, F                                     ; reg: 0x04e
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_153
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4f, 0x6                                   ; reg: 0x04f
        bsf     0x30, 0x3                                   ; reg: 0x030
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_153:                                                  ; address: 0x1088

        movf    0x4e, W                                     ; reg: 0x04e
        sublw   0x5a
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     (Common_RAM + 7), W                         ; reg: 0x077
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x2b                                        ; reg: 0x02b
        retlw   0x00
        movlw   0x07
        movwf   0x2d                                        ; reg: 0x02d
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_010
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x12
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_046
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_011
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x12
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_046
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x58, W                                     ; reg: 0x058
        sublw   0x1d
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_154
        bcf     0x2d, 0x1                                   ; reg: 0x02d
        bcf     0x2d, 0x2                                   ; reg: 0x02d

label_154:                                                  ; address: 0x10b4

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x53                                        ; reg: 0x053
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_011
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x027d
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x12
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_046
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x58, W                                     ; reg: 0x058
        sublw   0x1d
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_155
        bcf     0x2d, 0x0                                   ; reg: 0x02d
        bcf     0x2d, 0x2                                   ; reg: 0x02d

label_155:                                                  ; address: 0x10d0

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x53                                        ; reg: 0x053
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_011
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x53                                        ; reg: 0x053
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x027d
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x026a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        retlw   0x00

label_156:                                                  ; address: 0x10e0

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_044
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        sublw   0x43
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_181
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_044
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        sublw   0x57
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_164
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_045
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_045
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        movf    0x4a, W                                     ; reg: 0x04a
        addlw   0xf0
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_163
        addlw   0x10
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_193
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, F                                     ; reg: 0x04b
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_157
        clrf    0x42                                        ; reg: 0x042

label_157:                                                  ; address: 0x1115

        goto    label_163
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_028
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        clrf    PIR2                                        ; reg: 0x00d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movf    0x44, W                                     ; reg: 0x0c4
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEDATA                                      ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, WREN                                ; reg: 0x18c, bit: 2
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movf    INTCON, W                                   ; reg: 0x00b
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movlw   0x55
        movwf   EECON2                                      ; reg: 0x18d
        movlw   0xaa
        movwf   EECON2                                      ; reg: 0x18d
        bsf     EECON1, WR                                  ; reg: 0x18c, bit: 1
        btfsc   EECON1, WR                                  ; reg: 0x18c, bit: 1
        goto    0x0130
        bcf     EECON1, WREN                                ; reg: 0x18c, bit: 2
        movf    0x77, W                                     ; reg: 0x1f7
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        iorwf   INTCON, F                                   ; reg: 0x00b
        movlw   0x01
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movf    0x43, W                                     ; reg: 0x0c3
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEDATA                                      ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, WREN                                ; reg: 0x18c, bit: 2
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movf    INTCON, W                                   ; reg: 0x00b
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movlw   0x55
        movwf   EECON2                                      ; reg: 0x18d
        movlw   0xaa
        movwf   EECON2                                      ; reg: 0x18d
        bsf     EECON1, WR                                  ; reg: 0x18c, bit: 1
        btfsc   EECON1, WR                                  ; reg: 0x18c, bit: 1
        goto    0x014f
        bcf     EECON1, WREN                                ; reg: 0x18c, bit: 2
        movf    0x77, W                                     ; reg: 0x1f7
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        iorwf   INTCON, F                                   ; reg: 0x00b
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x071e
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        bsf     0x51, 0x3                                   ; reg: 0x051
        movlw   0x78
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x42                                        ; reg: 0x042
        goto    0x020c
        bcf     0x51, 0x3                                   ; reg: 0x051
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x019e
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        call    0x0000
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x026a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_048
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_163
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x29                                        ; reg: 0x029
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_163
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x4d                                        ; reg: 0x04d
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x57                                        ; reg: 0x057
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x56                                        ; reg: 0x056
        clrf    0x59                                        ; reg: 0x059
        movlw   0x18
        movwf   0x58                                        ; reg: 0x058
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_016
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4f                                        ; reg: 0x04f
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x53                                        ; reg: 0x053
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x52                                        ; reg: 0x052
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04ca
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        call    0x0090
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_048
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_163
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        swapf   0x4b, W                                     ; reg: 0x04b
        movwf   0x4e                                        ; reg: 0x04e
        movlw   0xf0
        andwf   0x4e, F                                     ; reg: 0x04e
        clrf    0x53                                        ; reg: 0x053
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x52                                        ; reg: 0x052
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_026
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x06a9
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        btfss   0x43, 0x5                                   ; reg: 0x043
        goto    0x01be
        movlw   0x21
        goto    0x01bf
        movlw   0x01
        movwf   0x43                                        ; reg: 0x043
        bsf     0x43, 0x5                                   ; reg: 0x043
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x020c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_049
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x82
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x42                                        ; reg: 0x042
        movlw   0x49

label_158:                                                  ; address: 0x11cc

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    label_159
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_158

label_159:                                                  ; address: 0x11d1

        movwf   TXREG                                       ; reg: 0x019
        movlw   0x0a

label_160:                                                  ; address: 0x11d3

        btfss   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    label_160
        movwf   TXREG                                       ; reg: 0x019
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_163
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x52                                        ; reg: 0x052
        bsf     0x5d, 0x7                                   ; reg: 0x05d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_163
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        sublw   0xc4
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_162
        clrf    0x4b                                        ; reg: 0x04b
        movf    0x4b, W                                     ; reg: 0x04b
        sublw   0x13
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_161
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_033
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x32
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x05cc
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x076e
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x32
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x05cc
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        incf    0x4b, F                                     ; reg: 0x04b
        goto    0x01e5

label_161:                                                  ; address: 0x1201

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    0x0203
        goto    0x0206
        clrf    PCLATH                                      ; reg: 0x00a
        goto    vector_reset
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_162:                                                  ; address: 0x120a

        goto    label_057
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_163:                                                  ; address: 0x120c

        goto    label_064

label_164:                                                  ; address: 0x120d

        movf    0x49, W                                     ; reg: 0x049
        sublw   0x52
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_063
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_045
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        clrf    0x4b                                        ; reg: 0x04b
        movf    0x4a, W                                     ; reg: 0x04a
        addlw   0xf1
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_180
        addlw   0x0f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_194
        clrf    0x53                                        ; reg: 0x053
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_180
        movf    0x53, W                                     ; reg: 0x053
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_047
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x4b                                        ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x51, 0x0                                   ; reg: 0x051
        goto    label_165
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_165:                                                  ; address: 0x1236

        btfss   0x51, 0x1                                   ; reg: 0x051
        goto    label_166
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x1                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_166:                                                  ; address: 0x123b

        btfss   0x51, 0x2                                   ; reg: 0x051
        goto    label_167
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x2                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_167:                                                  ; address: 0x1240

        btfss   0x51, 0x3                                   ; reg: 0x051
        goto    label_168
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x3                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_168:                                                  ; address: 0x1245

        btfss   PORTD, RD0                                  ; reg: 0x008, bit: 0
        goto    label_169
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x4                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_169:                                                  ; address: 0x124a

        btfss   PORTD, RD1                                  ; reg: 0x008, bit: 1
        goto    label_170
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x5                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_170:                                                  ; address: 0x124f

        btfss   PORTD, RD4                                  ; reg: 0x008, bit: 4
        goto    label_171
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x6                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_171:                                                  ; address: 0x1254

        btfss   PORTE, RE1                                  ; reg: 0x009, bit: 1
        goto    label_172
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x7                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_172:                                                  ; address: 0x1259

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_180
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x4b                                        ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   PORTB, RB1                                  ; reg: 0x006, bit: 1
        goto    label_173
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_173:                                                  ; address: 0x1263

        btfss   PORTB, RB5                                  ; reg: 0x006, bit: 5
        goto    label_174
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x1                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_174:                                                  ; address: 0x1268

        btfss   0x56, 0x5                                   ; reg: 0x056
        goto    label_175
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x2                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_175:                                                  ; address: 0x126d

        btfss   0x56, 0x7                                   ; reg: 0x056
        goto    label_176
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x3                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_176:                                                  ; address: 0x1272

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_180
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x22, W                                     ; reg: 0x022
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        movf    0x34, W                                     ; reg: 0x034
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x4b                                        ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x2d, 0x0                                   ; reg: 0x02d
        goto    label_177
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x0                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_177:                                                  ; address: 0x1284

        btfss   0x2d, 0x1                                   ; reg: 0x02d
        goto    label_178
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x1                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_178:                                                  ; address: 0x1289

        btfss   PORTB, RB4                                  ; reg: 0x006, bit: 4
        goto    label_179
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x4b, 0x2                                   ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_179:                                                  ; address: 0x128e

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_180
        rrf     0x45, W                                     ; reg: 0x045
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        rrf     0x44, W                                     ; reg: 0x044
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        rrf     (Common_RAM + 10), F                        ; reg: 0x07a
        rrf     (Common_RAM + 9), F                         ; reg: 0x079
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        movlw   0x07
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        movf    0x2e, W                                     ; reg: 0x02e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        movf    0x2f, W                                     ; reg: 0x02f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        movlw   0x02
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        movlw   0x71
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        goto    label_180
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x4b                                        ; reg: 0x04b
        goto    label_180
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x4b                                        ; reg: 0x04b
        goto    label_180
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_180:                                                  ; address: 0x12b9

        goto    label_187

label_181:                                                  ; address: 0x12ba

        movf    0x48, W                                     ; reg: 0x048
        sublw   0x41
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_186
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_044
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    0x49, W                                     ; reg: 0x049
        sublw   0x57
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_184
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_045
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_045
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x41
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_183
        movf    0x4a, W                                     ; reg: 0x04a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movf    0x4b, W                                     ; reg: 0x0cb
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEDATA                                      ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, WREN                                ; reg: 0x18c, bit: 2
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movf    INTCON, W                                   ; reg: 0x00b
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movlw   0x55
        movwf   EECON2                                      ; reg: 0x18d
        movlw   0xaa
        movwf   EECON2                                      ; reg: 0x18d
        bsf     EECON1, WR                                  ; reg: 0x18c, bit: 1

label_182:                                                  ; address: 0x12fa

        btfsc   PIR1, TMR2IF                                ; reg: 0x00c, bit: 1
        goto    label_182
        bcf     PIR1, CCP1IF                                ; reg: 0x00c, bit: 2
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        iorwf   INTCON, F                                   ; reg: 0x00b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4a, W                                     ; reg: 0x0ca
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, RD                                  ; reg: 0x18c, bit: 0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    EEDATA, W                                   ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   0x4b                                        ; reg: 0x0cb
        goto    label_183

label_183:                                                  ; address: 0x130f

        goto    label_187

label_184:                                                  ; address: 0x1310

        movf    0x49, W                                     ; reg: 0x049
        sublw   0x52
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_186
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_045
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x41
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_185
        movf    0x4a, W                                     ; reg: 0x04a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   EEADR                                       ; reg: 0x10d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     EECON1, EEPGD                               ; reg: 0x18c, bit: 7
        bsf     EECON1, RD                                  ; reg: 0x18c, bit: 0
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    EEDATA, W                                   ; reg: 0x10c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP1                                 ; reg: 0x003, bit: 6
        movwf   0x4b                                        ; reg: 0x0cb

label_185:                                                  ; address: 0x132d

        goto    label_187

label_186:                                                  ; address: 0x132e

        goto    label_192

label_187:                                                  ; address: 0x132f

        movf    0x48, W                                     ; reg: 0x048

label_188:                                                  ; address: 0x1330

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    label_189
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_188

label_189:                                                  ; address: 0x1335

        movwf   TXREG                                       ; reg: 0x019
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, W                                     ; reg: 0x049

label_190:                                                  ; address: 0x1338

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    label_191
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_190

label_191:                                                  ; address: 0x133d

        movwf   TXREG                                       ; reg: 0x019
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x56                                        ; reg: 0x056
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_013
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x56                                        ; reg: 0x056
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02ad
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x0a
        btfss   PIR1, TXIF                                  ; reg: 0x00c, bit: 4
        goto    0x034d
        movwf   TXREG                                       ; reg: 0x019
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movlw   0x01
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    0x0356

label_192:                                                  ; address: 0x1354

        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_243

label_193:                                                  ; address: 0x135a

        bsf     PCLATH, 0x0                                 ; reg: 0x00a
        bsf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        goto    label_250
        goto    label_251
        goto    label_260
        goto    label_261
        goto    label_263
        goto    label_265
        goto    label_266
        goto    label_267
        goto    label_268
        goto    label_271
        goto    label_277
        goto    label_278
        goto    label_279
        goto    label_281
        goto    label_284
        goto    label_286

label_194:                                                  ; address: 0x136e

        bsf     PCLATH, 0x0                                 ; reg: 0x00a
        bsf     PCLATH, 0x1                                 ; reg: 0x00a
        bcf     PCLATH, 0x2                                 ; reg: 0x00a
        addwf   PCL, F                                      ; reg: 0x002
        goto    label_287
        goto    label_288
        goto    label_289
        goto    label_291
        goto    label_295
        goto    label_296
        goto    label_297
        goto    label_298
        goto    label_299
        goto    label_300
        goto    label_301
        goto    label_303
        goto    label_304
        goto    label_305
        goto    label_306

function_051:                                               ; address: 0x1381

        clrf    0x4f                                        ; reg: 0x04f
        clrf    0x3b                                        ; reg: 0x03b
        bcf     0x30, 0x2                                   ; reg: 0x030
        clrf    0x3c                                        ; reg: 0x03c
        btfss   0x43, 0x5                                   ; reg: 0x043
        goto    label_317
        movlw   0x21
        goto    label_318
        movlw   0x01
        movwf   0x43                                        ; reg: 0x043
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_043
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        retlw   0x00
        btfss   (Common_RAM + 14), 0x6                      ; reg: 0x07e
        goto    label_196
        movlw   0x10
        movwf   0x4c                                        ; reg: 0x04c
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_136

label_195:                                                  ; address: 0x139a

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        btfsc   0x30, 0x6                                   ; reg: 0x030
        goto    label_196
        bsf     0x43, 0x5                                   ; reg: 0x043
        call    function_050
        bsf     PORTB, RB5                                  ; reg: 0x006, bit: 5
        movf    0x2b, W                                     ; reg: 0x02b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_046
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PORTB, RB5                                  ; reg: 0x006, bit: 5
        bsf     0x30, 0x6                                   ; reg: 0x030
        bcf     (Common_RAM + 14), 0x7                      ; reg: 0x07e
        bcf     (Common_RAM + 14), 0x6                      ; reg: 0x07e
        movlw   0x01
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    label_197

label_196:                                                  ; address: 0x13b1

        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078

label_197:                                                  ; address: 0x13b3

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_249

label_198:                                                  ; address: 0x13b6

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x4a, W                                     ; reg: 0x04a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    0x4a, F                                     ; reg: 0x04a

label_199:                                                  ; address: 0x13c2

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_326
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_325
        movf    0x49, W                                     ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_324
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_326
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_036
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_199
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_202

label_200:                                                  ; address: 0x13de

        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        btfsc   0x4f, 0x7                                   ; reg: 0x04f
        goto    label_206
        btfsc   0x43, 0x7                                   ; reg: 0x043
        goto    label_206
        bcf     0x43, 0x7                                   ; reg: 0x043
        bsf     0x43, 0x4                                   ; reg: 0x043

label_201:                                                  ; address: 0x13e6

        movf    0x4b, F                                     ; reg: 0x04b
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_205
        movf    0x4a, W                                     ; reg: 0x04a
        sublw   0x77
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_205
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_198

label_202:                                                  ; address: 0x13f2

        btfss   0x43, 0x7                                   ; reg: 0x043
        goto    label_203
        goto    label_205

label_203:                                                  ; address: 0x13f5

        bsf     PORTB, RB1                                  ; reg: 0x006, bit: 1
        btfss   0x5d, 0x7                                   ; reg: 0x05d
        goto    label_204
        btfss   0x5d, 0x5                                   ; reg: 0x05d
        goto    label_204
        goto    label_205

label_204:                                                  ; address: 0x13fb

        goto    label_201

label_205:                                                  ; address: 0x13fc

        bcf     PORTB, RB1                                  ; reg: 0x006, bit: 1

label_206:                                                  ; address: 0x13fd

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_256

function_052:                                               ; address: 0x1400

        call    function_061
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x0255
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        movlw   0x37
        movwf   0x2d                                        ; reg: 0x02d
        btfss   0x50, 0x1                                   ; reg: 0x050
        goto    0x040e
        movlw   0x47
        movwf   0x2d                                        ; reg: 0x02d
        bcf     0x50, 0x1                                   ; reg: 0x050
        goto    0x042f
        movlw   0x57
        movwf   0x2d                                        ; reg: 0x02d
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_040
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x3a, W                                     ; reg: 0x03a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_208
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_207
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x39, W                                     ; reg: 0x039
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_208

label_207:                                                  ; address: 0x1421

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_040
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x39, F                                     ; reg: 0x039
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 9), W                         ; reg: 0x079
        subwf   0x3a, F                                     ; reg: 0x03a
        goto    label_209

label_208:                                                  ; address: 0x142d

        clrf    0x3a                                        ; reg: 0x03a
        clrf    0x39                                        ; reg: 0x039

label_209:                                                  ; address: 0x142f

        movlw   0x67
        movwf   0x2d                                        ; reg: 0x02d
        retlw   0x00

function_053:                                               ; address: 0x1432

        movf    0x4d, W                                     ; reg: 0x04d
        sublw   0x01
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_210
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        movlw   0x01
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    label_214

label_210:                                                  ; address: 0x143a

        btfss   0x30, 0x2                                   ; reg: 0x030
        goto    label_211
        movlw   0x07
        movwf   0x2d                                        ; reg: 0x02d
        movlw   0x01
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    label_214

label_211:                                                  ; address: 0x1441

        movf    0x4f, W                                     ; reg: 0x04f
        andlw   0xf7
        sublw   0x40
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_212
        movf    0x4f, W                                     ; reg: 0x04f
        andlw   0xf7
        sublw   0x43
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_212
        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    label_214

label_212:                                                  ; address: 0x144e

        movf    0x4f, W                                     ; reg: 0x04f
        andlw   0xf7
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_213
        movlw   0x07
        movwf   0x2d                                        ; reg: 0x02d
        movlw   0x01
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    label_214

label_213:                                                  ; address: 0x1457

        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078

label_214:                                                  ; address: 0x1459

        retlw   0x00

label_215:                                                  ; address: 0x145a

        clrf    (Common_RAM + 7)                            ; reg: 0x077
        clrf    (Common_RAM + 8)                            ; reg: 0x078
        clrf    (Common_RAM + 9)                            ; reg: 0x079
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x60                                        ; reg: 0x060
        clrf    0x61                                        ; reg: 0x061
        clrf    0x62                                        ; reg: 0x062
        clrf    0x63                                        ; reg: 0x063
        movf    0x5f, W                                     ; reg: 0x05f
        iorwf   0x5e, W                                     ; reg: 0x05e
        iorwf   0x5d, W                                     ; reg: 0x05d
        iorwf   0x5c, W                                     ; reg: 0x05c
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_219
        movlw   0x20
        movwf   0x64                                        ; reg: 0x064

label_216:                                                  ; address: 0x146b

        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     0x58, F                                     ; reg: 0x058
        rlf     0x59, F                                     ; reg: 0x059
        rlf     0x5a, F                                     ; reg: 0x05a
        rlf     0x5b, F                                     ; reg: 0x05b
        rlf     0x60, F                                     ; reg: 0x060
        rlf     0x61, F                                     ; reg: 0x061
        rlf     0x62, F                                     ; reg: 0x062
        rlf     0x63, F                                     ; reg: 0x063
        movf    0x5f, W                                     ; reg: 0x05f
        subwf   0x63, W                                     ; reg: 0x063
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_217
        movf    0x5e, W                                     ; reg: 0x05e
        subwf   0x62, W                                     ; reg: 0x062
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_217
        movf    0x5d, W                                     ; reg: 0x05d
        subwf   0x61, W                                     ; reg: 0x061
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_217
        movf    0x5c, W                                     ; reg: 0x05c
        subwf   0x60, W                                     ; reg: 0x060

label_217:                                                  ; address: 0x1482

        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_218
        movf    0x5c, W                                     ; reg: 0x05c
        subwf   0x60, F                                     ; reg: 0x060
        movf    0x5d, W                                     ; reg: 0x05d
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x5d, W                                     ; reg: 0x05d
        subwf   0x61, F                                     ; reg: 0x061
        movf    0x5e, W                                     ; reg: 0x05e
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x5e, W                                     ; reg: 0x05e
        subwf   0x62, F                                     ; reg: 0x062
        movf    0x5f, W                                     ; reg: 0x05f
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x5f, W                                     ; reg: 0x05f
        subwf   0x63, F                                     ; reg: 0x063
        bsf     STATUS, C                                   ; reg: 0x003, bit: 0

label_218:                                                  ; address: 0x1493

        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        rlf     (Common_RAM + 8), F                         ; reg: 0x078
        rlf     (Common_RAM + 9), F                         ; reg: 0x079
        rlf     (Common_RAM + 10), F                        ; reg: 0x07a
        decfsz  0x64, F                                     ; reg: 0x064
        goto    label_216

label_219:                                                  ; address: 0x1499

        nop
        movlw   0xe0
        movwf   FSR                                         ; reg: 0x004
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_221

function_054:                                               ; address: 0x14a0

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x47                                        ; reg: 0x047
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x46                                        ; reg: 0x046
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     0x50, 0x4                                   ; reg: 0x050
        movf    0x6e, W                                     ; reg: 0x06e
        sublw   0x02
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_220
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        sublw   0x40
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_220
        movlw   0x6d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_017
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x58                                        ; reg: 0x058
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x58, W                                     ; reg: 0x058
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x50                                        ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     0x50, 0x4                                   ; reg: 0x050

label_220:                                                  ; address: 0x14cc

        btfss   (Common_RAM + 14), 0x0                      ; reg: 0x07e
        goto    0x053f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x52, W                                     ; reg: 0x052
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03d0
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x57                                        ; reg: 0x057
        movf    0x57, F                                     ; reg: 0x057
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04dd
        movlw   0x01
        movwf   0x57                                        ; reg: 0x057
        clrf    0x56                                        ; reg: 0x056
        clrf    0x55                                        ; reg: 0x055
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x54                                        ; reg: 0x054
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x56                                        ; reg: 0x056
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x55                                        ; reg: 0x055
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x54                                        ; reg: 0x054
        clrf    0x53                                        ; reg: 0x053
        rlf     0x54, F                                     ; reg: 0x054
        rlf     0x55, F                                     ; reg: 0x055
        rlf     0x56, F                                     ; reg: 0x056
        movf    0x56, W                                     ; reg: 0x056
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x5a                                        ; reg: 0x05a
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x59                                        ; reg: 0x059
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x58                                        ; reg: 0x058
        clrf    0x5f                                        ; reg: 0x05f
        clrf    0x5e                                        ; reg: 0x05e
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0x64
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_039
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x56                                        ; reg: 0x056
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x55                                        ; reg: 0x055
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x54                                        ; reg: 0x054
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        movwf   0x53                                        ; reg: 0x053
        movf    0x56, W                                     ; reg: 0x056
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x5a                                        ; reg: 0x05a
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x59                                        ; reg: 0x059
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x58                                        ; reg: 0x058
        clrf    0x5f                                        ; reg: 0x05f
        clrf    0x5e                                        ; reg: 0x05e
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x5c                                        ; reg: 0x05c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_215

label_221:                                                  ; address: 0x1519

        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x56                                        ; reg: 0x056
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   0x55                                        ; reg: 0x055
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x54                                        ; reg: 0x054
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        movwf   0x53                                        ; reg: 0x053
        movf    0x54, W                                     ; reg: 0x054
        movwf   0x53                                        ; reg: 0x053
        movf    0x55, W                                     ; reg: 0x055
        movwf   0x54                                        ; reg: 0x054
        movf    0x56, W                                     ; reg: 0x056
        movwf   0x55                                        ; reg: 0x055
        clrf    0x56                                        ; reg: 0x056
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     0x56, F                                     ; reg: 0x056
        rrf     0x55, F                                     ; reg: 0x055
        rrf     0x54, F                                     ; reg: 0x054
        rrf     0x53, F                                     ; reg: 0x053
        movf    0x56, F                                     ; reg: 0x056
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_222
        movf    0x55, W                                     ; reg: 0x055
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_223

label_222:                                                  ; address: 0x1535

        clrf    0x56                                        ; reg: 0x056
        clrf    0x55                                        ; reg: 0x055
        movlw   0xff
        movwf   0x54                                        ; reg: 0x054
        movwf   0x53                                        ; reg: 0x053

label_223:                                                  ; address: 0x153a

        movf    0x54, W                                     ; reg: 0x054
        movwf   0x51                                        ; reg: 0x051
        movf    0x53, W                                     ; reg: 0x053
        movwf   0x50                                        ; reg: 0x050
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x50, W                                     ; reg: 0x050
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x51, W                                     ; reg: 0x051
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_055:                                               ; address: 0x1546

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x51                                        ; reg: 0x051
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x50                                        ; reg: 0x050
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_054
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x51                                        ; reg: 0x051
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x50                                        ; reg: 0x050
        movf    0x51, W                                     ; reg: 0x051
        movwf   0x53                                        ; reg: 0x053
        movf    0x50, W                                     ; reg: 0x050
        movwf   0x52                                        ; reg: 0x052
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_026
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        retlw   0x00
        movf    (Common_RAM + 12), W                        ; reg: 0x07c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x006c
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        clrf    0x4e                                        ; reg: 0x04e
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x4d                                        ; reg: 0x04d
        movlw   0x58
        movwf   0x4f                                        ; reg: 0x04f
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0477
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x49                                        ; reg: 0x049
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x4f                                        ; reg: 0x04f
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x4e                                        ; reg: 0x04e
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0546
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        btfsc   (Common_RAM + 14), 0x5                      ; reg: 0x07e
        goto    0x059e
        movlw   0x01
        addwf   (Common_RAM + 12), W                        ; reg: 0x07c
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        incf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0072
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0072
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x059e
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x059a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x059e
        movf    (Common_RAM + 12), F                        ; reg: 0x07c
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x059e
        incf    (Common_RAM + 12), F                        ; reg: 0x07c
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_293

function_056:                                               ; address: 0x15a1

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x4d                                        ; reg: 0x04d
        clrf    0x4c                                        ; reg: 0x04c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x59, W                                     ; reg: 0x059
        sublw   0x09
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_346
        movf    0x59, W                                     ; reg: 0x059
        sublw   0x0a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4f                                        ; reg: 0x04f
        clrf    0x57                                        ; reg: 0x057
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x56                                        ; reg: 0x056
        clrf    0x59                                        ; reg: 0x059
        movlw   0x2d
        movwf   0x58                                        ; reg: 0x058
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_041
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4c                                        ; reg: 0x04c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movlw   0x40
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x4c, W                                     ; reg: 0x04c
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x4f                                        ; reg: 0x04f
        movlw   0x0b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        movlw   0x0c
        addwf   0x4f, F                                     ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x2d, 0x2                                   ; reg: 0x02d
        goto    0x05cd
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        movlw   0x00
        goto    0x05d0
        movlw   0x02
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movlw   0x1c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x4e, W                                     ; reg: 0x04e
        movwf   0x4a                                        ; reg: 0x04a
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x4b                                        ; reg: 0x04b
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 10), W                        ; reg: 0x07a
        addwf   0x4b, F                                     ; reg: 0x04b
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x54                                        ; reg: 0x054
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x53                                        ; reg: 0x053
        movlw   0x5b
        movwf   0x55                                        ; reg: 0x055
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0422
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4a                                        ; reg: 0x04a
        movf    0x48, W                                     ; reg: 0x048
        addwf   0x4a, F                                     ; reg: 0x04a
        movf    0x49, W                                     ; reg: 0x049
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  0x49, W                                     ; reg: 0x049
        addwf   0x4b, F                                     ; reg: 0x04b
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

label_224:                                                  ; address: 0x15f4

        call    0x0090
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_049
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_312

function_057:                                               ; address: 0x15fd

        movf    0x4f, W                                     ; reg: 0x04f
        andlw   0xf7
        andlw   0x43
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_357
        movlw   0x1c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        movlw   0x20
        movwf   0x4a                                        ; reg: 0x04a
        movlw   0x49
        movwf   0x4c                                        ; reg: 0x04c
        bcf     0x4d, 0x0                                   ; reg: 0x04d
        goto    label_361
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 13), W                        ; reg: 0x07d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4e                                        ; reg: 0x04e
        incf    0x4e, W                                     ; reg: 0x04e
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_037
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4e, W                                     ; reg: 0x04e
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0060
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x4b                                        ; reg: 0x04b
        movlw   0x59
        movwf   0x4c                                        ; reg: 0x04c
        bsf     0x4d, 0x0                                   ; reg: 0x04d
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x51                                        ; reg: 0x051
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x50                                        ; reg: 0x050
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x52                                        ; reg: 0x052
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x04a0
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x48                                        ; reg: 0x048
        btfss   0x4d, 0x0                                   ; reg: 0x04d
        goto    0x0642
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0xaa
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x03e7
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x48                                        ; reg: 0x048
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x53                                        ; reg: 0x053
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x52                                        ; reg: 0x052
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0624
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        retlw   0x00
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x4c, 0x4                                   ; reg: 0x04c
        goto    0x065c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, F                                     ; reg: 0x048
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x065b
        movf    (Common_RAM + 5), W                         ; reg: 0x075
        subwf   (Common_RAM + 6), W                         ; reg: 0x076
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x065b
        decf    0x48, F                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6d, F                                     ; reg: 0x06d
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x067f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0045
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        btfsc   0x22, 0x7                                   ; reg: 0x022
        goto    0x0674
        movf    0x22, W                                     ; reg: 0x022
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0674
        rrf     0x22, W                                     ; reg: 0x022
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        rrf     (Common_RAM + 7), F                         ; reg: 0x077
        movlw   0x3f
        andwf   (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        goto    0x0675
        movlw   0x00
        addwf   0x49, W                                     ; reg: 0x049
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x57, W                                     ; reg: 0x057
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x067c
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x067f
        movlw   0x01
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    0x0681
        movlw   0x00
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_327

function_058:                                               ; address: 0x1684

        btfss   (Common_RAM + 14), 0x0                      ; reg: 0x07e
        goto    0x06a5
        movlw   0x63
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_042
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    0x48, F                                     ; reg: 0x048
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0699
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        goto    0x069a
        decf    0x48, F                                     ; reg: 0x048
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x07
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x06a0
        movlw   0x03
        movwf   0x48                                        ; reg: 0x048
        movf    0x48, W                                     ; reg: 0x048
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        goto    0x06a9
        goto    0x06a9
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movlw   0x03
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x06a9
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        retlw   0x00

function_059:                                               ; address: 0x16ab

        movlw   0xff
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        clrf    0x49                                        ; reg: 0x049
        clrf    0x48                                        ; reg: 0x048
        movf    0x48, W                                     ; reg: 0x048
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x06c7
        movlw   0x63
        addwf   0x48, W                                     ; reg: 0x048
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        movwf   0x4b                                        ; reg: 0x04b
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x06bf
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x4a                                        ; reg: 0x04a
        movf    0x4b, W                                     ; reg: 0x04b
        subwf   0x49, W                                     ; reg: 0x049
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x06c5
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x49                                        ; reg: 0x049
        incf    0x48, F                                     ; reg: 0x048
        goto    0x06b0
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   0x49, F                                     ; reg: 0x049
        movf    (Common_RAM + 6), W                         ; reg: 0x076
        movwf   0x48                                        ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfss   0x50, 0x0                                   ; reg: 0x050
        goto    0x06d3
        movlw   0xd0
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movlw   0x02
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        goto    0x0717
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, W                                     ; reg: 0x049
        sublw   0x02
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x06e0
        movlw   0x10
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movlw   0x0e
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    0x0717
        goto    0x0717
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    (Common_RAM + 5), W                         ; reg: 0x075
        subwf   (Common_RAM + 6), W                         ; reg: 0x076
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0711
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_040
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4c                                        ; reg: 0x04c
        rrf     0x4d, W                                     ; reg: 0x04d
        movwf   0x4f                                        ; reg: 0x04f
        rrf     0x4c, W                                     ; reg: 0x04c
        movwf   0x4e                                        ; reg: 0x04e
        rrf     0x4f, F                                     ; reg: 0x04f
        rrf     0x4e, F                                     ; reg: 0x04e
        rrf     0x4f, F                                     ; reg: 0x04f
        rrf     0x4e, F                                     ; reg: 0x04e
        movlw   0x1f
        andwf   0x4f, F                                     ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x3a, W                                     ; reg: 0x03a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4f, W                                     ; reg: 0x04f
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_227
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_226
        movf    0x4e, W                                     ; reg: 0x04e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x39, W                                     ; reg: 0x039
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_225
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_227

label_225:                                                  ; address: 0x1708

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_226:                                                  ; address: 0x1709

        movlw   0x70
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movlw   0x08
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_228
        goto    label_228
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_227:                                                  ; address: 0x1711

        movlw   0x38
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movlw   0x04
        movwf   (Common_RAM + 9)                            ; reg: 0x079
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_228

label_228:                                                  ; address: 0x1717

        retlw   0x00
        movf    0x6b, W                                     ; reg: 0x06b
        subwf   0x57, W                                     ; reg: 0x057
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_229
        movf    0x57, W                                     ; reg: 0x057
        goto    label_230

label_229:                                                  ; address: 0x171e

        movf    0x6b, W                                     ; reg: 0x06b

label_230:                                                  ; address: 0x171f

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        clrf    0x48                                        ; reg: 0x048
        movlw   0x08
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6c, W                                     ; reg: 0x06c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_014
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x09
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 6), W                         ; reg: 0x076
        subwf   (Common_RAM + 5), W                         ; reg: 0x075
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x073b
        incf    0x4c, F                                     ; reg: 0x04c
        incf    (Common_RAM + 5), F                         ; reg: 0x075
        movf    (Common_RAM + 5), W                         ; reg: 0x075
        subwf   (Common_RAM + 6), W                         ; reg: 0x076
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0771
        decf    0x4c, F                                     ; reg: 0x04c
        decf    (Common_RAM + 5), F                         ; reg: 0x075
        movf    0x62, W                                     ; reg: 0x062
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4d                                        ; reg: 0x04d
        movf    0x4d, F                                     ; reg: 0x04d
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0749
        movlw   0x08
        movwf   0x4d                                        ; reg: 0x04d
        decf    0x4d, F                                     ; reg: 0x04d
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4c, F                                     ; reg: 0x04c
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0751
        movlw   0x08
        movwf   0x4c                                        ; reg: 0x04c
        decf    0x4c, F                                     ; reg: 0x04c
        movlw   0x63
        addwf   0x4c, W                                     ; reg: 0x04c
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        movwf   0x4f                                        ; reg: 0x04f
        movlw   0x63
        addwf   0x4d, W                                     ; reg: 0x04d
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        movwf   0x50                                        ; reg: 0x050
        movf    0x4f, W                                     ; reg: 0x04f
        subwf   0x50, W                                     ; reg: 0x050
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0770
        movf    0x50, W                                     ; reg: 0x050
        subwf   0x4f, W                                     ; reg: 0x04f
        movwf   0x48                                        ; reg: 0x048
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0770
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    0x48, W                                     ; reg: 0x048
        subwf   INDF, W                                     ; reg: 0x000
        movwf   INDF                                        ; reg: 0x000
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        goto    0x0764
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6c, W                                     ; reg: 0x06c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4b, W                                     ; reg: 0x04b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07bb
        movf    0x4b, W                                     ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6c, W                                     ; reg: 0x06c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        clrf    0x4a                                        ; reg: 0x04a
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x078e
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        movwf   0x4f                                        ; reg: 0x04f
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   0x4f, W                                     ; reg: 0x04f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x078c
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x4a                                        ; reg: 0x04a
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        goto    0x077d
        movf    0x4b, W                                     ; reg: 0x04b
        subwf   0x4a, W                                     ; reg: 0x04a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0794
        clrf    0x48                                        ; reg: 0x048
        goto    0x079d
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6c, W                                     ; reg: 0x06c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4a, W                                     ; reg: 0x04a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x079d
        movf    0x4b, W                                     ; reg: 0x04b
        subwf   0x4a, W                                     ; reg: 0x04a
        movwf   0x48                                        ; reg: 0x048
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07b1
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        subwf   0x48, W                                     ; reg: 0x048
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07af
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    0x48, W                                     ; reg: 0x048
        subwf   INDF, W                                     ; reg: 0x000
        movwf   INDF                                        ; reg: 0x000
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        goto    0x079e
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6b, W                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x48, W                                     ; reg: 0x048
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07bb
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6b, F                                     ; reg: 0x06b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4b, W                                     ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6c, W                                     ; reg: 0x06c
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07e5
        movf    0x6c, W                                     ; reg: 0x06c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x4b, W                                     ; reg: 0x04b
        movwf   0x48                                        ; reg: 0x048
        clrf    (Common_RAM + 4)                            ; reg: 0x074
        movf    (Common_RAM + 4), W                         ; reg: 0x074
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07db
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    INDF, W                                     ; reg: 0x000
        movwf   0x51                                        ; reg: 0x051
        movf    0x48, W                                     ; reg: 0x048
        sublw   0xff
        subwf   0x51, W                                     ; reg: 0x051
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07d9
        movlw   0x63
        addwf   (Common_RAM + 4), W                         ; reg: 0x074
        movwf   FSR                                         ; reg: 0x004
        movf    0x48, W                                     ; reg: 0x048
        addwf   INDF, W                                     ; reg: 0x000
        movwf   INDF                                        ; reg: 0x000
        incf    (Common_RAM + 4), F                         ; reg: 0x074
        goto    0x07c5
        movf    0x48, W                                     ; reg: 0x048
        sublw   0xff
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x6b, W                                     ; reg: 0x06b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x07e5
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        addwf   0x6b, F                                     ; reg: 0x06b
        movlw   0x0a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x02bc
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

function_060:                                               ; address: 0x17ef

        movf    0x4b, W                                     ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x6c                                        ; reg: 0x06c
        retlw   0x00

        ; code

        org     0x1800

function_061:                                               ; address: 0x1800

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4f, W                                     ; reg: 0x04f
        sublw   0xc2
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0007
        movlw   0xc3
        movwf   0x4f                                        ; reg: 0x04f
        clrf    0x5b                                        ; reg: 0x05b
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movlw   0xa4
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_018
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4f                                        ; reg: 0x04f
        movf    0x4e, W                                     ; reg: 0x04e
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x4d, W                                     ; reg: 0x04d
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5d                                        ; reg: 0x05d
        movf    0x4f, W                                     ; reg: 0x04f
        movwf   0x5c                                        ; reg: 0x05c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_018
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        retlw   0x00
        clrf    FSR                                         ; reg: 0x004
        movlw   0x1f
        andwf   STATUS, F                                   ; reg: 0x003
        movlw   0x20
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   TXREG                                       ; reg: 0x019
        movlw   0x26
        movwf   RCSTA                                       ; reg: 0x018
        movlw   0x90
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   RCSTA                                       ; reg: 0x018
        movlw   0x18
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   SSPBUF                                      ; reg: 0x013
        movlw   0x28
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   SSPCON                                      ; reg: 0x014
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     SSPCON, WCOL                                ; reg: 0x014, bit: 7
        bcf     SSPCON, SSPOV                               ; reg: 0x014, bit: 6
        bsf     ADCON0, ADON                                ; reg: 0x01f, bit: 0
        bsf     ADCON0, 0x1                                 ; reg: 0x01f
        bsf     ADCON0, GO                                  ; reg: 0x01f, bit: 2
        bcf     ADCON0, CHS0                                ; reg: 0x01f, bit: 3
        movlw   0x07
        movwf   CCPR2H                                      ; reg: 0x01c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_060

label_231:                                                  ; address: 0x1843

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        clrf    0x32                                        ; reg: 0x032
        clrf    0x31                                        ; reg: 0x031
        clrf    0x4c                                        ; reg: 0x04c
        clrf    0x3a                                        ; reg: 0x03a
        clrf    0x39                                        ; reg: 0x039
        clrf    0x4f                                        ; reg: 0x04f
        clrf    0x5e                                        ; reg: 0x05e
        clrf    0x5f                                        ; reg: 0x05f
        clrf    0x60                                        ; reg: 0x060
        clrf    0x6f                                        ; reg: 0x06f
        clrf    0x50                                        ; reg: 0x050
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_009
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        clrf    (Common_RAM + 14)                           ; reg: 0x07e
        clrf    (Common_RAM + 5)                            ; reg: 0x075

label_232:                                                  ; address: 0x1857

        movf    (Common_RAM + 5), W                         ; reg: 0x075
        sublw   0x06
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_233
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_015
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        incf    (Common_RAM + 5), F                         ; reg: 0x075
        goto    label_232

label_233:                                                  ; address: 0x1862

        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_023
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_072

label_234:                                                  ; address: 0x186e

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x05
        movwf   0x45                                        ; reg: 0x045
        movlw   0x14
        movwf   0x44                                        ; reg: 0x044
        clrf    0x47                                        ; reg: 0x047
        clrf    0x46                                        ; reg: 0x046
        movlw   0x1c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movlw   0x20
        movwf   0x52                                        ; reg: 0x052
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_026
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_027
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        btfss   0x43, 0x5                                   ; reg: 0x043
        goto    label_235
        movlw   0x21
        goto    label_236

label_235:                                                  ; address: 0x188a

        movlw   0x01

label_236:                                                  ; address: 0x188b

        movwf   0x43                                        ; reg: 0x043
        bsf     0x43, 0x5                                   ; reg: 0x043
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_031
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x40                                        ; reg: 0x040
        clrf    0x41                                        ; reg: 0x041
        bsf     PIR1, RCIF                                  ; reg: 0x00c, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bsf     RCSTA, SPEN                                 ; reg: 0x018, bit: 7
        bsf     RCSTA, CREN                                 ; reg: 0x018, bit: 4

label_237:                                                  ; address: 0x1899

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_036
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    0x041b

label_238:                                                  ; address: 0x189e

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x04c3
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    0x0502

label_239:                                                  ; address: 0x18a4

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        btfss   Common_RAM, 0x1                             ; reg: 0x070
        goto    0x00c0
        incf    Common_RAM, F                               ; reg: 0x070
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x42, F                                     ; reg: 0x042
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x00be
        movf    0x42, W                                     ; reg: 0x042
        sublw   0x79
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x00b7
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_012
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        decf    0x42, F                                     ; reg: 0x042
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_134

label_240:                                                  ; address: 0x18bb

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_241
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     0x51, 0x3                                   ; reg: 0x051

label_241:                                                  ; address: 0x18c0

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        goto    label_135

label_242:                                                  ; address: 0x18c2

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_245
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_156

label_243:                                                  ; address: 0x18c8

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_245
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x42, W                                     ; reg: 0x042
        sublw   0x77
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_244
        movlw   0x78
        movwf   0x42                                        ; reg: 0x042

label_244:                                                  ; address: 0x18d3

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        goto    label_237

label_245:                                                  ; address: 0x18d5

        movf    Common_RAM, W                               ; reg: 0x070
        sublw   0xf0
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_246
        clrf    Common_RAM                                  ; reg: 0x070
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_031
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_246:                                                  ; address: 0x18df

        btfss   0x51, 0x3                                   ; reg: 0x051
        goto    label_247
        goto    label_237

label_247:                                                  ; address: 0x18e2

        btfss   0x5d, 0x7                                   ; reg: 0x05d
        goto    label_248
        btfss   0x5d, 0x6                                   ; reg: 0x05d
        goto    label_248
        bcf     0x5d, 0x7                                   ; reg: 0x05d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_051
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x4c, W                                     ; reg: 0x04c
        sublw   0x2f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x00ef
        goto    0x0122
        btfss   0x30, 0x3                                   ; reg: 0x030
        goto    0x00f2
        goto    0x0122

label_248:                                                  ; address: 0x18f2

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x0391

label_249:                                                  ; address: 0x18f4

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x00f9
        goto    0x0122
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x70
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0113
        xorlw   0x10
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0150
        xorlw   0x30
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x01a7
        xorlw   0x10
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0227
        xorlw   0x70
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0400
        xorlw   0x10
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0400
        xorlw   0x30
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x053e
        xorlw   0x10

label_250:                                                  ; address: 0x1910

        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x065d
        goto    0x065d

function_062:                                               ; address: 0x1913

        movf    0x4b, F                                     ; reg: 0x04b
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x011a

label_251:                                                  ; address: 0x1916

        movf    0x4a, W                                     ; reg: 0x04a
        sublw   0x0b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x065d
        movf    0x57, W                                     ; reg: 0x057
        sublw   0x09
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x011f
        bsf     0x4f, 0x0                                   ; reg: 0x04f
        goto    0x0122
        goto    0x065d

label_252:                                                  ; address: 0x1921

        bsf     0x4f, 0x1                                   ; reg: 0x04f

label_253:                                                  ; address: 0x1922

        btfsc   0x5d, 0x6                                   ; reg: 0x05d
        goto    0x012b
        btfsc   0x30, 0x2                                   ; reg: 0x030
        goto    0x012b
        movf    0x4f, W                                     ; reg: 0x04f
        andlw   0xf7
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x012b
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        bcf     0x5d, 0x6                                   ; reg: 0x05d
        btfss   0x50, 0x5                                   ; reg: 0x050
        goto    0x0132
        movlw   0x07
        andwf   0x4c, F                                     ; reg: 0x04c
        bsf     0x4c, 0x4                                   ; reg: 0x04c
        goto    0x0134
        movlw   0x10
        movwf   0x4c                                        ; reg: 0x04c
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_012
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        btfss   0x2d, 0x7                                   ; reg: 0x02d
        goto    label_254
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_010
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_255

label_254:                                                  ; address: 0x1941

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_048
        bsf     PCLATH, 0x4                                 ; reg: 0x00a

label_255:                                                  ; address: 0x1944

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_200

label_256:                                                  ; address: 0x1946

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     0x43, 0x5                                   ; reg: 0x043
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        btfss   0x50, 0x5                                   ; reg: 0x050
        goto    label_257
        movlw   0x07
        andwf   0x5d, F                                     ; reg: 0x05d
        goto    label_258

label_257:                                                  ; address: 0x194f

        clrf    0x5d                                        ; reg: 0x05d

label_258:                                                  ; address: 0x1950

        movlw   0x07
        movwf   0x2d                                        ; reg: 0x02d
        btfss   0x5d, 0x7                                   ; reg: 0x05d
        goto    label_259
        btfss   0x5d, 0x5                                   ; reg: 0x05d
        goto    label_259
        goto    label_283

label_259:                                                  ; address: 0x1957

        btfss   0x56, 0x5                                   ; reg: 0x056
        goto    label_264
        movf    0x4b, W                                     ; reg: 0x04b
        sublw   0x00

label_260:                                                  ; address: 0x195b

        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_264
        xorlw   0xff
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_262

label_261:                                                  ; address: 0x1960

        movf    0x4a, W                                     ; reg: 0x04a
        sublw   0x68
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_264

label_262:                                                  ; address: 0x1964

        bcf     PCLATH, 0x4                                 ; reg: 0x00a

label_263:                                                  ; address: 0x1965

        call    function_048
        bsf     PCLATH, 0x4                                 ; reg: 0x00a

label_264:                                                  ; address: 0x1967

        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_023

label_265:                                                  ; address: 0x196e

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x57, W                                     ; reg: 0x057

label_266:                                                  ; address: 0x1971

        sublw   0x13
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_267
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a

label_267:                                                  ; address: 0x1976

        movf    0x4b, W                                     ; reg: 0x04b
        sublw   0x15
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_270
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_269
        movf    0x4a, W                                     ; reg: 0x04a

label_268:                                                  ; address: 0x197d

        sublw   0x17
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_270

label_269:                                                  ; address: 0x1980

        goto    label_371

label_270:                                                  ; address: 0x1981

        movf    0x57, W                                     ; reg: 0x057
        sublw   0x13

label_271:                                                  ; address: 0x1983

        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_272
        goto    label_371

label_272:                                                  ; address: 0x1986

        btfss   0x56, 0x5                                   ; reg: 0x056
        goto    label_273
        goto    label_371

label_273:                                                  ; address: 0x1989

        btfss   0x50, 0x5                                   ; reg: 0x050
        goto    label_274
        movlw   0x07
        andwf   0x4c, F                                     ; reg: 0x04c
        bsf     0x4c, 0x5                                   ; reg: 0x04c
        goto    label_275

label_274:                                                  ; address: 0x198f

        movlw   0x20
        movwf   0x4c                                        ; reg: 0x04c

label_275:                                                  ; address: 0x1991

        btfsc   0x30, 0x3                                   ; reg: 0x030
        goto    label_276
        btfsc   0x30, 0x6                                   ; reg: 0x030
        goto    label_276
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_052
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0400
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_276:                                                  ; address: 0x199b

        btfsc   0x51, 0x3                                   ; reg: 0x051
        goto    0x01a0
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_048
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a

label_277:                                                  ; address: 0x19a1

        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_007
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        btfsc   0x4c, 0x3                                   ; reg: 0x04c
        goto    label_280

label_278:                                                  ; address: 0x19a9

        btfss   0x50, 0x5                                   ; reg: 0x050
        goto    label_280
        movlw   0x6a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_017
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_280

label_279:                                                  ; address: 0x19b7

        goto    label_283

label_280:                                                  ; address: 0x19b8

        btfsc   0x5d, 0x5                                   ; reg: 0x05d
        goto    label_282
        bcf     0x5d, 0x3                                   ; reg: 0x05d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x49                                        ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_022
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_281:                                                  ; address: 0x19c3

        movlw   0x2a
        movwf   0x4b                                        ; reg: 0x04b
        movlw   0x30
        movwf   0x4a                                        ; reg: 0x04a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_012
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_371

label_282:                                                  ; address: 0x19cd

        btfss   0x5d, 0x7                                   ; reg: 0x05d
        goto    label_371
        bcf     0x30, 0x6                                   ; reg: 0x030

label_283:                                                  ; address: 0x19d0

        bcf     0x50, 0x4                                   ; reg: 0x050
        bcf     (Common_RAM + 14), 0x4                      ; reg: 0x07e
        bcf     (Common_RAM + 14), 0x5                      ; reg: 0x07e
        movlw   0xdc
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x5f                                        ; reg: 0x05f
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x42                                        ; reg: 0x042

label_284:                                                  ; address: 0x19d8

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        bcf     0x51, 0x3                                   ; reg: 0x051
        clrf    0x4d                                        ; reg: 0x04d
        clrf    0x30                                        ; reg: 0x030

function_063:                                               ; address: 0x19dc

        clrf    0x4c                                        ; reg: 0x04c

label_285:                                                  ; address: 0x19dd

        movlw   0x07
        movwf   0x2d                                        ; reg: 0x02d

label_286:                                                  ; address: 0x19df

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x49                                        ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_022
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_012
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     0x43, 0x5                                   ; reg: 0x043
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_051
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     (Common_RAM + 14), 0x4                      ; reg: 0x07e
        bcf     (Common_RAM + 14), 0x5                      ; reg: 0x07e
        movlw   0xdc
        movwf   0x5a                                        ; reg: 0x05a
        btfss   0x5d, 0x5                                   ; reg: 0x05d
        goto    0x01f7
        bsf     0x5d, 0x3                                   ; reg: 0x05d
        incf    0x4d, F                                     ; reg: 0x04d
        btfss   0x50, 0x4                                   ; reg: 0x050
        goto    0x01fc
        movlw   0x04
        movwf   0x4d                                        ; reg: 0x04d
        movlw   0x30
        iorwf   0x4c, F                                     ; reg: 0x04c
        movlw   0x03
        movwf   (Common_RAM + 12)                           ; reg: 0x07c
        movf    (Common_RAM + 12), F                        ; reg: 0x07c
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x020b
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0400
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        btfss   0x30, 0x3                                   ; reg: 0x030
        goto    0x0209
        incf    0x4d, F                                     ; reg: 0x04d
        decf    (Common_RAM + 12), F                        ; reg: 0x07c
        goto    0x0200
        bcf     0x5d, 0x5                                   ; reg: 0x05d
        bcf     0x5d, 0x7                                   ; reg: 0x05d
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        clrf    (Common_RAM + 12)                           ; reg: 0x07c
        clrf    (Common_RAM + 13)                           ; reg: 0x07d
        bcf     0x51, 0x7                                   ; reg: 0x051
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0432
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x021c
        btfsc   0x5d, 0x6                                   ; reg: 0x05d
        goto    0x021c
        btfss   0x30, 0x3                                   ; reg: 0x030
        goto    0x0220
        btfsc   0x5d, 0x6                                   ; reg: 0x05d
        goto    0x021f
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        goto    0x0122
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a

label_287:                                                  ; address: 0x1a22

        movlw   0x1c
        movwf   (Common_RAM + 2)                            ; reg: 0x072
        movlw   0x20

label_288:                                                  ; address: 0x1a25

        movwf   (Common_RAM + 1)                            ; reg: 0x071
        bsf     PORTB, RB1                                  ; reg: 0x006, bit: 1
        bcf     (Common_RAM + 14), 0x7                      ; reg: 0x07e
        btfss   0x2d, 0x7                                   ; reg: 0x02d

label_289:                                                  ; address: 0x1a29

        goto    0x0238
        btfsc   (Common_RAM + 14), 0x4                      ; reg: 0x07e
        goto    0x0238
        movlw   0x1c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        movlw   0x20
        movwf   0x52                                        ; reg: 0x052
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_026
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_290
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 13), W                        ; reg: 0x07d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        incf    0x48, W                                     ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_001
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_001
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x4a                                        ; reg: 0x04a
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x4d                                        ; reg: 0x04d
        movlw   0x59
        movwf   0x4f                                        ; reg: 0x04f
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_055
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_290:                                                  ; address: 0x1a59

        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0xf8

label_291:                                                  ; address: 0x1a5b

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        btfss   (Common_RAM + 14), 0x4                      ; reg: 0x07e

label_292:                                                  ; address: 0x1a5e

        goto    0x0261
        movlw   0x01
        goto    0x0262
        movlw   0x00
        addwf   0x48, W                                     ; reg: 0x048
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4c                                        ; reg: 0x04c
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x055d

label_293:                                                  ; address: 0x1a67

        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_294:                                                  ; address: 0x1a68

        btfss   0x2d, 0x7                                   ; reg: 0x02d
        goto    0x029a
        movlw   0x23
        addwf   0x5a, W                                     ; reg: 0x05a
        subwf   0x57, W                                     ; reg: 0x057
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x029a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x029a
        btfsc   (Common_RAM + 14), 0x4                      ; reg: 0x07e
        goto    0x029a
        bsf     (Common_RAM + 14), 0x4                      ; reg: 0x07e

label_295:                                                  ; address: 0x1a74

        btfss   0x2d, 0x2                                   ; reg: 0x02d
        goto    0x0279
        clrf    (Common_RAM + 10)                           ; reg: 0x07a
        movlw   0x00

label_296:                                                  ; address: 0x1a78

        goto    0x027c
        movlw   0x02
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movlw   0x1c

label_297:                                                  ; address: 0x1a7c

        addlw   0xd0
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x49                                        ; reg: 0x049
        movlw   0x02
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        movlw   0x03
        addwf   0x49, F                                     ; reg: 0x049
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x54                                        ; reg: 0x054
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x53                                        ; reg: 0x053
        movlw   0x5b
        movwf   0x55                                        ; reg: 0x055
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_019
        bsf     PCLATH, 0x4                                 ; reg: 0x00a

label_298:                                                  ; address: 0x1a90

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        addwf   0x4a, W                                     ; reg: 0x04a
        movwf   0x5b                                        ; reg: 0x05b
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x5c                                        ; reg: 0x05c
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 9), W                         ; reg: 0x079
        addwf   0x5c, F                                     ; reg: 0x05c
        btfsc   (Common_RAM + 14), 0x4                      ; reg: 0x07e
        goto    label_302
        movlw   0x04
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_299:                                                  ; address: 0x1a9e

        movwf   0x49                                        ; reg: 0x049
        movlw   0x5c
        movwf   0x48                                        ; reg: 0x048
        bcf     PCLATH, 0x3                                 ; reg: 0x00a

label_300:                                                  ; address: 0x1aa2

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_056
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079

label_301:                                                  ; address: 0x1aa6

        movwf   0x5c                                        ; reg: 0x05c
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x5b                                        ; reg: 0x05b

label_302:                                                  ; address: 0x1aa9

        movf    0x5c, W                                     ; reg: 0x05c

label_303:                                                  ; address: 0x1aaa

        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x02dd
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2

label_304:                                                  ; address: 0x1aae

        goto    0x02b3
        movf    0x5b, W                                     ; reg: 0x05b
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0

label_305:                                                  ; address: 0x1ab2

        goto    0x02dd
        btfss   0x2d, 0x7                                   ; reg: 0x02d
        goto    0x02bb

label_306:                                                  ; address: 0x1ab5

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_012
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     (Common_RAM + 14), 0x5                      ; reg: 0x07e
        movlw   0x5a
        addwf   0x5b, W                                     ; reg: 0x05b
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    0x5c, W                                     ; reg: 0x05c
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        incf    (Common_RAM + 10), F                        ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_309
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_307
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_309

label_307:                                                  ; address: 0x1acc

        btfss   0x56, 0x5                                   ; reg: 0x056
        goto    label_308
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_048
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     0x5d, 0x5                                   ; reg: 0x05d
        bcf     0x5d, 0x7                                   ; reg: 0x05d
        goto    0x02dc

label_308:                                                  ; address: 0x1ad4

        btfss   0x5d, 0x7                                   ; reg: 0x05d
        goto    0x02dc
        btfss   0x5d, 0x5                                   ; reg: 0x05d
        goto    0x02dc
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_050
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x065d

label_309:                                                  ; address: 0x1adc

        goto    0x031e
        movf    0x4b, W                                     ; reg: 0x04b
        sublw   0x03
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x031e
        xorlw   0xff
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x02e8
        movf    0x4a, W                                     ; reg: 0x04a
        sublw   0x37
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x031e
        movf    0x4b, W                                     ; reg: 0x04b
        sublw   0x04
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x031e
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x02f2
        movf    0x4a, W                                     ; reg: 0x04a
        sublw   0x97
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x031e
        btfsc   0x56, 0x5                                   ; reg: 0x056
        goto    0x02f9
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_010
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x4b, W                                     ; reg: 0x04b
        sublw   0x03
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_314
        xorlw   0xff
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_310
        movf    0x4a, W                                     ; reg: 0x04a
        sublw   0x5b
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_314

label_310:                                                  ; address: 0x1b04

        btfsc   0x2d, 0x7                                   ; reg: 0x02d
        goto    label_314
        btfsc   0x2d, 0x0                                   ; reg: 0x02d
        goto    label_311
        btfss   0x2d, 0x1                                   ; reg: 0x02d
        goto    label_314

label_311:                                                  ; address: 0x1b0a

        btfsc   (Common_RAM + 14), 0x5                      ; reg: 0x07e
        goto    label_314
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    label_224

label_312:                                                  ; address: 0x1b0e

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x5a                                        ; reg: 0x05a
        movf    0x5a, W                                     ; reg: 0x05a
        sublw   0x96
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_313
        movlw   0x96
        movwf   0x5a                                        ; reg: 0x05a

label_313:                                                  ; address: 0x1b17

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x22, W                                     ; reg: 0x022
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x59                                        ; reg: 0x059
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_057
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_314:                                                  ; address: 0x1b1e

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x49                                        ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_022
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_053
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x032d
        goto    0x0122
        movf    (Common_RAM + 13), W                        ; reg: 0x07d
        sublw   0x02
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0358
        movlw   0x01
        addwf   (Common_RAM + 13), W                        ; reg: 0x07d
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        incf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_000
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_000
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 8)                            ; reg: 0x078
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_316
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_315
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_316

label_315:                                                  ; address: 0x1b54

        incf    (Common_RAM + 13), F                        ; reg: 0x07d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_057
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_316:                                                  ; address: 0x1b58

        movlw   0x07
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movlw   0x08
        movwf   0x48                                        ; reg: 0x048
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x05a1
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    0x4b, W                                     ; reg: 0x04b
        subwf   (Common_RAM + 10), W                        ; reg: 0x07a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x036f
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x036d
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   (Common_RAM + 8), W                         ; reg: 0x078
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x036f
        clrf    0x60                                        ; reg: 0x060
        goto    0x065d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        btfsc   0x22, 0x7                                   ; reg: 0x022
        goto    0x0379
        movf    0x22, W                                     ; reg: 0x022
        sublw   0x00
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0379
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rrf     0x22, W                                     ; reg: 0x022
        goto    0x037a
        movlw   0x00
        addlw   0x3c
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        subwf   0x57, W                                     ; reg: 0x057
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0381
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x039e
        movf    0x60, W                                     ; reg: 0x060
        sublw   0x04
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x039d
        movlw   0x6e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a

label_317:                                                  ; address: 0x1b89

        bcf     PCLATH, 0x3                                 ; reg: 0x00a

label_318:                                                  ; address: 0x1b8a

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_017
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_319
        movlw   0x00
        goto    label_320

label_319:                                                  ; address: 0x1b93

        movlw   0x01

label_320:                                                  ; address: 0x1b94

        andlw   0x02
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_321
        movf    0x4d, W                                     ; reg: 0x04d
        sublw   0x01
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_321
        goto    label_285

label_321:                                                  ; address: 0x1b9c

        goto    label_252
        goto    label_323
        movf    0x57, W                                     ; reg: 0x057
        sublw   0xfd
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_322
        clrf    0x60                                        ; reg: 0x060
        goto    label_323

label_322:                                                  ; address: 0x1ba4

        movf    0x60, W                                     ; reg: 0x060
        sublw   0x38
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_323
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        bsf     0x30, 0x2                                   ; reg: 0x030
        movlw   0xb4
        movwf   0x5f                                        ; reg: 0x05f
        goto    label_253

label_323:                                                  ; address: 0x1bad

        movlw   0x0b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movlw   0x40
        movwf   0x48                                        ; reg: 0x048
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_056
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    0x4b, W                                     ; reg: 0x04b
        subwf   (Common_RAM + 10), W                        ; reg: 0x07a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03c3
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x03c2
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   (Common_RAM + 8), W                         ; reg: 0x078
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03c3
        goto    0x065d
        movlw   0x01
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_022
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movlw   0x0c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movlw   0xa8
        movwf   0x48                                        ; reg: 0x048

label_324:                                                  ; address: 0x1bd1

        bcf     PCLATH, 0x3                                 ; reg: 0x00a

label_325:                                                  ; address: 0x1bd2

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_056
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    0x4b, W                                     ; reg: 0x04b
        subwf   (Common_RAM + 10), W                        ; reg: 0x07a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0

label_326:                                                  ; address: 0x1bda

        goto    0x03e2
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x03e1
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   (Common_RAM + 8), W                         ; reg: 0x078
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03e2
        goto    0x065d
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        btfss   0x50, 0x5                                   ; reg: 0x050
        goto    0x03ed
        movf    0x5d, W                                     ; reg: 0x05d

function_064:                                               ; address: 0x1be7

        andlw   0x07
        andwf   0x4c, F                                     ; reg: 0x04c
        movlw   0x50
        iorwf   0x4c, F                                     ; reg: 0x04c
        bcf     0x50, 0x5                                   ; reg: 0x050
        goto    0x03ef
        movlw   0x53
        movwf   0x4c                                        ; reg: 0x04c
        bcf     (Common_RAM + 14), 0x4                      ; reg: 0x07e
        clrf    (Common_RAM + 5)                            ; reg: 0x075
        movf    (Common_RAM + 5), W                         ; reg: 0x075
        sublw   0x07
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x03fc
        movlw   0x63
        addwf   (Common_RAM + 5), W                         ; reg: 0x075
        movwf   FSR                                         ; reg: 0x004
        movf    0x57, W                                     ; reg: 0x057
        movwf   INDF                                        ; reg: 0x000
        incf    (Common_RAM + 5), F                         ; reg: 0x075
        goto    0x03f1
        movlw   0xff
        movwf   0x5a                                        ; reg: 0x05a
        clrf    0x6c                                        ; reg: 0x06c
        goto    0x065d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x49                                        ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_022
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        incf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_002
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_002
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x4b                                        ; reg: 0x04b
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        addlw   0x48
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x4d                                        ; reg: 0x04d
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x4f                                        ; reg: 0x04f
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_055
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        btfss   0x5d, 0x7                                   ; reg: 0x05d
        goto    0x043c
        btfss   0x5d, 0x5                                   ; reg: 0x05d
        goto    0x043c
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0000
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x065d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0432
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0443
        goto    0x0122
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x064b

label_327:                                                  ; address: 0x1c45

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0471
        btfsc   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    0x044f
        movf    0x6e, W                                     ; reg: 0x06e
        sublw   0x0f
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0454
        bsf     0x4f, 0x1                                   ; reg: 0x04f
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        bsf     (Common_RAM + 14), 0x6                      ; reg: 0x07e
        bcf     0x30, 0x6                                   ; reg: 0x030
        goto    0x00f2
        movf    0x60, W                                     ; reg: 0x060
        sublw   0x04
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0470
        movf    0x4d, W                                     ; reg: 0x04d
        sublw   0x01
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x046f
        movlw   0x6e
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_017
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), F                         ; reg: 0x078
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_328
        movlw   0x00
        goto    label_329

label_328:                                                  ; address: 0x1c6a

        movlw   0x01

label_329:                                                  ; address: 0x1c6b

        andlw   0x02
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_330
        goto    label_285

label_330:                                                  ; address: 0x1c6f

        goto    label_252
        goto    label_332
        movf    0x57, W                                     ; reg: 0x057
        sublw   0xfd
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_331
        clrf    0x60                                        ; reg: 0x060
        goto    label_332

label_331:                                                  ; address: 0x1c77

        movf    0x60, W                                     ; reg: 0x060
        sublw   0x38
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_332
        bsf     0x4f, 0x2                                   ; reg: 0x04f
        bsf     0x4f, 0x4                                   ; reg: 0x04f
        bsf     0x30, 0x0                                   ; reg: 0x030
        goto    label_253

label_332:                                                  ; address: 0x1c7f

        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        movwf   (Common_RAM + 5)                            ; reg: 0x075
        movf    0x5d, W                                     ; reg: 0x05d
        andlw   0x07
        movwf   (Common_RAM + 6)                            ; reg: 0x076
        btfss   0x50, 0x1                                   ; reg: 0x050
        goto    label_333
        movlw   0x17
        movwf   0x2d                                        ; reg: 0x02d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_058
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   (Common_RAM + 5), W                         ; reg: 0x075
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0493
        btfsc   0x4c, 0x4                                   ; reg: 0x04c
        goto    0x0493
        goto    0x050a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0684
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   (Common_RAM + 6)                            ; reg: 0x076
        goto    0x04b4

label_333:                                                  ; address: 0x1c99

        btfss   0x4c, 0x3                                   ; reg: 0x04c
        goto    0x04b4
        movlw   0x6a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x5a                                        ; reg: 0x05a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_017
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   (Common_RAM + 6)                            ; reg: 0x076
        movf    (Common_RAM + 6), F                         ; reg: 0x076
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_335
        movf    (Common_RAM + 5), F                         ; reg: 0x075
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_334
        bsf     0x50, 0x5                                   ; reg: 0x050
        goto    label_253

label_334:                                                  ; address: 0x1cae

        goto    label_336

label_335:                                                  ; address: 0x1caf

        decf    (Common_RAM + 6), F                         ; reg: 0x076

label_336:                                                  ; address: 0x1cb0

        movf    (Common_RAM + 6), W                         ; reg: 0x076
        subwf   (Common_RAM + 5), W                         ; reg: 0x075
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_337

label_337:                                                  ; address: 0x1cb4

        btfss   (Common_RAM + 14), 0x7                      ; reg: 0x07e
        goto    label_338
        goto    label_371

label_338:                                                  ; address: 0x1cb7

        btfss   0x4c, 0x4                                   ; reg: 0x04c
        goto    label_344
        movf    0x6c, F                                     ; reg: 0x06c
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_340
        movf    0x57, W                                     ; reg: 0x057
        movwf   0x6c                                        ; reg: 0x06c
        movlw   0x0b
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x53                                        ; reg: 0x053
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x6c, W                                     ; reg: 0x06c
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x54                                        ; reg: 0x054
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_014

label_339:                                                  ; address: 0x1cc9

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_340:                                                  ; address: 0x1ccb

        movf    (Common_RAM + 6), W                         ; reg: 0x076
        subwf   (Common_RAM + 5), W                         ; reg: 0x075
        btfsc   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    label_343
        bcf     PCLATH, 0x3                                 ; reg: 0x00a

label_341:                                                  ; address: 0x1cd0

        call    function_059
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    0x4b, W                                     ; reg: 0x04b
        subwf   (Common_RAM + 10), W                        ; reg: 0x07a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04e0
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04de

label_342:                                                  ; address: 0x1cda

        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x4a, W                                     ; reg: 0x04a
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x04e0
        goto    0x065d
        goto    0x04e3
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0718
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        goto    0x04e5

label_343:                                                  ; address: 0x1ce4

        goto    0x04ee
        goto    0x04ec

label_344:                                                  ; address: 0x1ce6

        movf    (Common_RAM + 6), W                         ; reg: 0x076
        subwf   (Common_RAM + 5), W                         ; reg: 0x075
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x04eb
        goto    0x065d
        goto    0x04ee
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        bsf     0x4c, 0x4                                   ; reg: 0x04c
        movf    (Common_RAM + 6), W                         ; reg: 0x076
        subwf   (Common_RAM + 5), W                         ; reg: 0x075
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0507
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x06ab
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0507
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0502
        movf    0x4a, W                                     ; reg: 0x04a
        subwf   (Common_RAM + 8), W                         ; reg: 0x078
        btfsc   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0507
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    0x0718
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     0x4c, 0x4                                   ; reg: 0x04c
        clrf    0x6c                                        ; reg: 0x06c
        bcf     0x5d, 0x4                                   ; reg: 0x05d
        bcf     0x5d, 0x7                                   ; reg: 0x05d
        goto    0x065d
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        clrf    (Common_RAM + 12)                           ; reg: 0x07c
        clrf    (Common_RAM + 13)                           ; reg: 0x07d
        bcf     0x51, 0x7                                   ; reg: 0x051
        bsf     (Common_RAM + 14), 0x4                      ; reg: 0x07e
        movlw   0x8f
        andwf   0x4c, F                                     ; reg: 0x04c
        movlw   0x60
        iorwf   0x4c, F                                     ; reg: 0x04c
        bcf     0x51, 0x4                                   ; reg: 0x051
        bcf     INTCON, PEIE                                ; reg: 0x00b, bit: 6
        bcf     INTCON, GIE                                 ; reg: 0x00b, bit: 7
        btfsc   INTCON, GIE                                 ; reg: 0x00b, bit: 7
        goto    0x0516
        clrf    (Common_RAM + 2)                            ; reg: 0x072
        clrf    (Common_RAM + 1)                            ; reg: 0x071
        movlw   0xc0
        iorwf   INTCON, F                                   ; reg: 0x00b
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 13), W                        ; reg: 0x07d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        incf    0x48, W                                     ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_004
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_004
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x4a                                        ; reg: 0x04a
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x4d                                        ; reg: 0x04d
        movlw   0x61
        movwf   0x4f                                        ; reg: 0x04f
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_055
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        clrf    0x49                                        ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_022
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    0x5d, W                                     ; reg: 0x05d
        andlw   0x07
        movwf   (Common_RAM + 6)                            ; reg: 0x076
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_058
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_005
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        clrf    0x4e                                        ; reg: 0x04e
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x4d                                        ; reg: 0x04d
        movlw   0x60
        movwf   0x4f                                        ; reg: 0x04f
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_020
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4b                                        ; reg: 0x04b
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        movwf   0x4a                                        ; reg: 0x04a
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x4f                                        ; reg: 0x04f
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x4e                                        ; reg: 0x04e
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_021
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movf    (Common_RAM + 13), W                        ; reg: 0x07d
        sublw   0x01
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    label_350
        movlw   0x01
        addwf   (Common_RAM + 13), W                        ; reg: 0x07d
        movwf   (Common_RAM + 7)                            ; reg: 0x077
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 7), F                         ; reg: 0x077
        movf    (Common_RAM + 7), W                         ; reg: 0x077
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        incf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_003
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x49, W                                     ; reg: 0x049
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_003
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4a                                        ; reg: 0x04a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x4b                                        ; reg: 0x04b
        movlw   0x62
        movwf   0x56                                        ; reg: 0x056
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_038
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x4c                                        ; reg: 0x04c
        movf    0x4b, W                                     ; reg: 0x04b
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x4a, W                                     ; reg: 0x04a
        movwf   0x4d                                        ; reg: 0x04d
        movf    0x4c, W                                     ; reg: 0x04c
        movwf   0x4f                                        ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0000
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x05d2
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x05ab
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x05d2
        incf    (Common_RAM + 13), F                        ; reg: 0x07d
        movf    (Common_RAM + 13), W                        ; reg: 0x07d
        sublw   0x02
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x05b1
        bcf     (Common_RAM + 14), 0x4                      ; reg: 0x07e
        bcf     STATUS, C                                   ; reg: 0x003, bit: 0
        rlf     (Common_RAM + 13), W                        ; reg: 0x07d
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        incf    0x48, W                                     ; reg: 0x048

label_345:                                                  ; address: 0x1db6

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_004
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        movwf   (Common_RAM + 10)                           ; reg: 0x07a

label_346:                                                  ; address: 0x1dbd

        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movf    0x48, W                                     ; reg: 0x048

label_347:                                                  ; address: 0x1dbf

        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_004
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x49                                        ; reg: 0x049
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        movwf   0x4a                                        ; reg: 0x04a
        movwf   0x4e                                        ; reg: 0x04e
        movf    0x49, W                                     ; reg: 0x049
        movwf   0x4d                                        ; reg: 0x04d
        movlw   0x61
        movwf   0x4f                                        ; reg: 0x04f

label_348:                                                  ; address: 0x1dce

        bcf     PCLATH, 0x3                                 ; reg: 0x00a

label_349:                                                  ; address: 0x1dcf

        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_055
        bsf     PCLATH, 0x3                                 ; reg: 0x00a

label_350:                                                  ; address: 0x1dd2

        btfsc   PORTD, RD1                                  ; reg: 0x008, bit: 1
        goto    0x05d8
        btfsc   0x4f, 0x3                                   ; reg: 0x04f
        goto    0x05d8
        btfss   0x30, 0x0                                   ; reg: 0x030
        goto    0x05da

label_351:                                                  ; address: 0x1dd8

        bsf     0x51, 0x4                                   ; reg: 0x051
        goto    0x05db
        bcf     0x51, 0x4                                   ; reg: 0x051
        movlw   0x62
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x56                                        ; reg: 0x056
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    function_038
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movlw   0x04
        movwf   0x4e                                        ; reg: 0x04e

label_352:                                                  ; address: 0x1de7

        movlw   0xb0

label_353:                                                  ; address: 0x1de8

        movwf   0x4d                                        ; reg: 0x04d
        movf    0x48, W                                     ; reg: 0x048
        movwf   0x4f                                        ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0000
        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0632
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2

label_354:                                                  ; address: 0x1df4

        goto    0x05f9
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x0632
        btfsc   0x51, 0x7                                   ; reg: 0x051
        goto    0x0632
        bsf     0x51, 0x7                                   ; reg: 0x051
        movlw   0x27
        movwf   0x2d                                        ; reg: 0x02d
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_050

label_355:                                                  ; address: 0x1e00

        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     PCLATH, 0x3                                 ; reg: 0x00a
        call    function_009
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        bsf     PCLATH, 0x3                                 ; reg: 0x00a
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        movlw   0x37

label_356:                                                  ; address: 0x1e09

        movwf   0x2d                                        ; reg: 0x02d
        btfss   0x50, 0x1                                   ; reg: 0x050
        goto    label_358

label_357:                                                  ; address: 0x1e0c

        movlw   0x47
        movwf   0x2d                                        ; reg: 0x02d
        bcf     0x50, 0x1                                   ; reg: 0x050
        goto    label_363

label_358:                                                  ; address: 0x1e10

        movlw   0x57
        movwf   0x2d                                        ; reg: 0x02d
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    function_040
        bsf     PCLATH, 0x4                                 ; reg: 0x00a

label_359:                                                  ; address: 0x1e15

        movf    (Common_RAM + 9), W                         ; reg: 0x079
        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x3a, W                                     ; reg: 0x03a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x062b
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0621
        movf    (Common_RAM + 8), W                         ; reg: 0x078

label_360:                                                  ; address: 0x1e1e

        subwf   0x39, W                                     ; reg: 0x039
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x062b
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x0113

label_361:                                                  ; address: 0x1e23

        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movf    (Common_RAM + 8), W                         ; reg: 0x078
        subwf   0x39, F                                     ; reg: 0x039
        movf    (Common_RAM + 9), W                         ; reg: 0x079

label_362:                                                  ; address: 0x1e27

        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        incfsz  (Common_RAM + 9), W                         ; reg: 0x079
        subwf   0x3a, F                                     ; reg: 0x03a
        goto    0x062d
        clrf    0x3a                                        ; reg: 0x03a
        clrf    0x39                                        ; reg: 0x039

label_363:                                                  ; address: 0x1e2d

        movlw   0x67
        movwf   0x2d                                        ; reg: 0x02d
        movlw   0x77

label_364:                                                  ; address: 0x1e30

        movwf   0x2d                                        ; reg: 0x02d
        clrf    0x4d                                        ; reg: 0x04d
        movlw   0x62
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5

label_365:                                                  ; address: 0x1e34

        movwf   0x56                                        ; reg: 0x056
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x00ca

label_366:                                                  ; address: 0x1e38

        bsf     PCLATH, 0x4                                 ; reg: 0x00a

label_367:                                                  ; address: 0x1e39

        movf    (Common_RAM + 8), W                         ; reg: 0x078
        bsf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        movwf   0x48                                        ; reg: 0x048
        movlw   0x05
        movwf   0x4e                                        ; reg: 0x04e
        movlw   0x28
        movwf   0x4d                                        ; reg: 0x04d
        movf    0x48, W                                     ; reg: 0x048

label_368:                                                  ; address: 0x1e41

        movwf   0x4f                                        ; reg: 0x04f
        bcf     STATUS, RP0                                 ; reg: 0x003, bit: 5
        call    0x0000
        movf    (Common_RAM + 9), W                         ; reg: 0x079

label_369:                                                  ; address: 0x1e45

        movwf   (Common_RAM + 10)                           ; reg: 0x07a
        movf    (Common_RAM + 10), W                        ; reg: 0x07a
        subwf   0x4b, W                                     ; reg: 0x04b
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x065c
        btfss   STATUS, Z                                   ; reg: 0x003, bit: 2
        goto    0x0650
        movf    (Common_RAM + 8), W                         ; reg: 0x078

label_370:                                                  ; address: 0x1e4d

        subwf   0x4a, W                                     ; reg: 0x04a
        btfss   STATUS, C                                   ; reg: 0x003, bit: 0
        goto    0x065c
        clrf    0x4b                                        ; reg: 0x04b
        clrf    0x4a                                        ; reg: 0x04a
        bcf     PCLATH, 0x4                                 ; reg: 0x00a
        call    0x07d3
        bsf     PCLATH, 0x4                                 ; reg: 0x00a
        movlw   0x8f
        andwf   0x4c, F                                     ; reg: 0x04c
        movlw   0x50
        iorwf   0x4c, F                                     ; reg: 0x04c
        movf    0x4c, W                                     ; reg: 0x04c
        andlw   0x07
        movwf   (Common_RAM + 5)                            ; reg: 0x075
        goto    0x065d

label_371:                                                  ; address: 0x1e5d

        goto    0x0099
        sleep

        end
