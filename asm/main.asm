; Sugoro Quest++ Dicenics English patch. Assemble: asar --fix-checksum=off asm/main.asm ROM
; (build.py writes build/en_font.bin and build/en_widths.bin first)
lorom

; ---------------------------------------------------------------------------------------------------------------
; VWF for the main text engine. The reader stores the glyph code in $18C5 and calls the 12 px cell renderer
; $08:8281, then INC $18B7 (cell index). We draw 8x16 2bpp proportional glyphs instead, OR-ing them into the
; same 4bpp box buffer ($7E:3684, VRAM base from $84A2[style]) and keep $18B7 = line start cell + ceil(px / 12),
; so newline ({nl} looks up $869C by cell) and page logic keep working. Cell layout: pairs of cells = 3 tiles,
; even cell at pos[cell + 1] (table $84C2[style], word offsets into the buffer).
; ---------------------------------------------------------------------------------------------------------------
org $088121
    JSL vwf_draw            ; was JSL $088281

; state: the old 12 px glyph scratch ($7E:3604-$3683) is unused once the hook is in
!VX     = $7E3604           ; pixel x in the current line
!LSTART = $7E3606           ; cell index of the line start
!VCELL  = $7E3608           ; $18B7 value we expect on the next call (else: new line)
!NCLR   = $7E360A           ; tiles of this line already cleared
!GW     = $7E360C           ; glyph advance
!CODE   = $7E360E
!SHIFT  = $7E3610
!TIDX   = $7E3612
!TA     = $7E3614           ; word offset of the tile holding VX
!TB     = $7E3616           ; word offset of the next tile
!WITHIN = $7E3618

org $3A8000
en_font:
    incbin "../build/en_font.bin"       ; 256 x 32 bytes: 16 rows x (plane0, plane1)
en_widths:
    incbin "../build/en_widths.bin"     ; 256 bytes

vwf_draw:
    PHP
    PHB
    REP #$30
    PEA $7E7E
    PLB
    PLB
    LDA $18B5
    ASL A
    TAX
    LDA.l $0884A2,x
    STA $BF                 ; VRAM word base of the box
    LDA.l $0884C2,x
    STA $BB                 ; [$BB] = $08:pos table
    LDA #$0008
    STA $BD

    LDA $18B7
    BEQ .reset
    CMP.l !VCELL
    BEQ .cont
.reset:
    STA.l !LSTART
    LDA #$0000
    STA.l !VX
    STA.l !NCLR
.cont:
    LDA $18C5
    AND #$00FF
    STA.l !CODE
    ; codes $88-$9B ({at0}..{at19}): move to cell N of the line (choice columns), draw nothing
    SEC
    SBC #$0088
    CMP #$0014
    BCS .glyph
    STA $B5
    ASL A
    CLC
    ADC $B5                 ; N * 3
    ASL A
    ASL A                   ; N * 12
    CMP.l !VX
    BCC +
    STA.l !VX
+   LDA #$0000
    STA.l !GW
    JMP .advance
.glyph:
    LDA.l !CODE
    TAX
    LDA.l en_widths,x
    AND #$00FF
    STA.l !GW

    LDA.l !VX
    LSR A
    LSR A
    LSR A
    STA.l !TIDX
    JSR tile_off
    STA.l !TA
    LDA.l !TIDX
    INC A
    JSR tile_off
    STA.l !TB

    ; zero tiles the first time this line touches them
    LDA.l !TIDX
    CMP.l !NCLR
    BCC .a_ok
    LDA.l !TA
    JSR clear_tile
    LDA.l !TIDX
    INC A
    STA.l !NCLR
.a_ok:
    LDA.l !TIDX
    INC A
    CMP.l !NCLR
    BCC .b_ok
    LDA.l !TB
    JSR clear_tile
    LDA.l !TIDX
    INC A
    INC A
    STA.l !NCLR
.b_ok:

    ; render 16 rows: each plane byte shifted right by VX & 7, high part -> tile A, spill -> tile B
    LDA.l !TA
    ASL A
    CLC
    ADC #$3684
    STA $B7
    LDA.l !TB
    ASL A
    CLC
    ADC #$3684
    STA $B9
    LDA.l !VX
    AND #$0007
    STA.l !SHIFT
    LDA.l !CODE
    ASL A
    ASL A
    ASL A
    ASL A
    ASL A
    TAX
    LDY #$0000
.row:
    TYA
    AND #$0007
    ASL A
    STA $B5                 ; byte offset of the row in a tile
    TYA
    AND #$0008
    BEQ .top
    LDA $B5
    ORA #$0200              ; rows 8-15: the tile row below
    STA $B5
.top:
    LDA.l en_font,x
    AND #$00FF
    XBA
    JSR shift
    JSR or_ab
    INC $B5
    LDA.l en_font+1,x
    AND #$00FF
    XBA
    JSR shift
    JSR or_ab
    INX
    INX
    INY
    CPY #$0010
    BNE .row

    LDA.l !TA
    JSR dma_tile
    LDA.l !TB
    JSR dma_tile

    ; advance; $18B7 = LSTART + ceil(VX / 12) - 1 (the caller increments it)
.advance:
    LDA.l !VX
    CLC
    ADC.l !GW
    STA.l !VX
    LDX #$0000
.ceil:
    CMP #$0001
    BCC .ceil_done
    INX
    CMP #$000D
    BCC .ceil_done
    SEC
    SBC #$000C
    BRA .ceil
.ceil_done:
    TXA
    CLC
    ADC.l !LSTART
    STA.l !VCELL
    DEC A
    STA $18B7
    PLB
    PLP
    RTL

; A = tile index in the line -> A = word offset in the box buffer
tile_off:
    LDX #$0000
.div:
    CMP #$0003
    BCC .got
    SBC #$0003
    INX
    BRA .div
.got:
    ASL A
    ASL A
    ASL A
    ASL A
    STA.l !WITHIN
    TXA
    ASL A
    CLC
    ADC.l !LSTART
    INC A
    ASL A
    TAY
    LDA [$BB],y
    CLC
    ADC.l !WITHIN
    RTS

; A >>= SHIFT (16-bit)
shift:
    PHX
    PHA
    LDA.l !SHIFT
    TAX
    PLA
    CPX #$0000
    BEQ .done
.loop:
    LSR A
    DEX
    BNE .loop
.done:
    PLX
    RTS

; A = shifted row: high byte ORed into ($B7)+$B5, low byte into ($B9)+$B5
or_ab:
    PHY
    LDY $B5
    SEP #$20
    XBA
    ORA ($B7),y
    STA ($B7),y
    XBA
    ORA ($B9),y
    STA ($B9),y
    REP #$20
    PLY
    RTS

; A = word offset: zero that 4bpp tile and the one below it (+$200 bytes)
clear_tile:
    PHX
    PHY
    ASL A
    CLC
    ADC #$3684
    TAY
    LDX #$0010
    LDA #$0000
.clr:
    STA $0000,y
    STA $0200,y
    INY
    INY
    DEX
    BNE .clr
    PLY
    PLX
    RTS

; A = word offset: queue the tile and the one below it for VRAM ($0089E9: A = bytes, X = src, Y = VRAM word)
dma_tile:
    STA $B5
.top:
    LDA $B5
    ASL A
    CLC
    ADC #$3684
    TAX
    LDA $B5
    CLC
    ADC $BF
    TAY
    LDA #$0020
    JSL $0089E9
    BCS .top
.bottom:
    LDA $B5
    ASL A
    CLC
    ADC #$3884
    TAX
    LDA $B5
    CLC
    ADC $BF
    CLC
    ADC #$0100
    TAY
    LDA #$0020
    JSL $0089E9
    BCS .bottom
    RTS

; ---------------------------------------------------------------------------------------------------------------
; Status-panel strings ($07:AF68 loop: 8 px cell = one 2bpp tile per char, row table at ($B1)). We draw two 3 px
; condensed glyphs per tile (cond_font = 8 bytes per text code, ink at bits 7-5). $9D counts chars left in the row:
; the row start doubles the cell count, odd $9D = left half, even = right half (shift 4, then next tile, 32 bytes).
; ---------------------------------------------------------------------------------------------------------------
pushpc
org $07AF80
    JSL cond_rowstart       ; was AND #$00FF : STA $9D
    NOP
org $07AFCF
    JSL cond_draw           ; was JSR $B00D : INC $9F : $99 += $10 : DEC $9D
    NOP #11
pullpc

cond_font:
    incbin "../build/cond8_font.bin"

cond_rowstart:
    AND #$00FF
    ASL A
    INC A
    STA $9D
    RTL

cond_draw:
    PHP
    REP #$30
    PHB
    PHX
    PHY
    LDA $A1
    AND #$00FF
    ASL A
    ASL A
    ASL A
    TAX
    LDY #$0000
    PEA $7E7E
    PLB
    PLB
.row:
    LDA.l cond_font,x
    AND #$00FF
    PHA
    LDA $9D
    LSR A
    PLA
    BCS .or                 ; odd $9D = left half
    LSR A
    LSR A
    LSR A
    LSR A
.or:
    ORA ($99),y
    STA ($99),y
    INX
    INY
    INY
    CPY #$0010
    BCC .row
    LDA $9D
    LSR A
    BCS .left
    LDA $99
    CLC
    ADC #$0020
    STA $99
.left:
    INC $9F
    DEC $9D
    PLY
    PLX
    PLB
    PLP
    RTL

warnpc $3AAFFF
