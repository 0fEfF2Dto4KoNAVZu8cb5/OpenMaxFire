/**
 * Native ESP32-S3 USB 2.0 device port.
 *
 * This is a self-powered device interface. USB VBUS is used only for presence
 * detection through a MOSFET gate; there is intentionally no conductive power
 * path from VBUS to V5_MAIN, V3V3_MAIN, or any other board supply rail.
 */

const UsbDataEsd = () => (
	<chip
		name="U201"
		manufacturerPartNumber="TPD2EUSB30DRTR"
		supplierPartNumbers={{ jlcpcb: ["C97502"] }}
		datasheetUrl="https://www.ti.com/lit/ds/symlink/tpd2eusb30.pdf"
		pinLabels={{
			pin1: "D_POS",
			pin2: "D_NEG",
			pin3: "GND",
		}}
		// Exact C97502 EasyEDA geometry imported with `tsci import --use-exact-footprint`.
		// PRODUCTION GATE: compare the generated paste/mask/copper against TI DRT
		// and the assembler's C97502 library before releasing fabrication outputs.
		footprint={
			<footprint>
				<smtpad
					portHints={["pin1"]}
					pcbX="0.499999mm"
					pcbY="-0.350012mm"
					width="0.2999994mm"
					height="0.1999996mm"
					shape="rect"
				/>
				<smtpad
					portHints={["pin2"]}
					pcbX="0.499999mm"
					pcbY="0.350012mm"
					width="0.2999994mm"
					height="0.1999996mm"
					shape="rect"
				/>
				<smtpad
					portHints={["pin3"]}
					pcbX="-0.499999mm"
					pcbY="0mm"
					width="0.2999994mm"
					height="0.1999996mm"
					shape="rect"
				/>
				<courtyardoutline
					outline={[
						{ x: -0.910527, y: 0.758 },
						{ x: 1.113473, y: 0.758 },
						{ x: 1.113473, y: -0.7834 },
						{ x: -0.910527, y: -0.7834 },
						{ x: -0.910527, y: 0.758 },
					]}
				/>
			</footprint>
		}
		pcbX={56.5}
		pcbY={39.5}
		schX={28}
		schY={0}
		schSectionName="USB"
	/>
);

/*
 * USB4105 recommended land pattern, drawn from GCT drawing USB4105 rev B4.
 *
 * The parts-engine footprint previously used here duplicated each 0.65 mm
 * locating hole as both a pcb_hole and a pcb_cutout.  A locating peg is an
 * ordinary non-plated through hole, so the duplicate cutouts made placement
 * DRC report the connector body overlapping its own holes.  Keeping the NPTHs
 * as <hole> primitives preserves the drill geometry without weakening DRC.
 *
 * The footprint origin intentionally matches the former fetched footprint.
 * Copper, slot and NPTH dimensions below follow the manufacturer's recommended
 * PCB layout rather than the rounded EasyEDA land pattern.  In this local
 * frame, the drawing's PCB-edge line is y = -5.225 mm.
 */
const Usb4105Footprint = () => (
	<footprint insertionDirection="from_bottom">
		{/* Four 0.60 x 1.15 mm power/ground lands. */}
		<smtpad
			portHints={["pin17", "GND1", "A1B12"]}
			pcbX={-3.2}
			pcbY={2.125}
			width={0.6}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin18", "VBUS1", "A4B9"]}
			pcbX={-2.4}
			pcbY={2.125}
			width={0.6}
			height={1.15}
			shape="rect"
		/>

		{/* Eight 0.30 x 1.15 mm signal lands on 0.50 mm pitch. */}
		<smtpad
			portHints={["pin19", "SBU2", "B8"]}
			pcbX={-1.75}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin20", "CC1", "A5"]}
			pcbX={-1.25}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin21", "DM2", "B7", "Dn2"]}
			pcbX={-0.75}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin22", "DP1", "A6", "Dp1"]}
			pcbX={-0.25}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin23", "DM1", "A7", "Dn1"]}
			pcbX={0.25}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin24", "DP2", "B6", "Dp2"]}
			pcbX={0.75}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin25", "SBU1", "A8"]}
			pcbX={1.25}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin26", "CC2", "B5"]}
			pcbX={1.75}
			pcbY={2.125}
			width={0.3}
			height={1.15}
			shape="rect"
		/>

		<smtpad
			portHints={["pin27", "VBUS2", "B4A9"]}
			pcbX={2.4}
			pcbY={2.125}
			width={0.6}
			height={1.15}
			shape="rect"
		/>
		<smtpad
			portHints={["pin28", "GND2", "B1A12"]}
			pcbX={3.2}
			pcbY={2.125}
			width={0.6}
			height={1.15}
			shape="rect"
		/>

		{/* Shell stakes: 1.00 mm copper width around the specified 0.60 mm slots. */}
		<platedhole
			portHints={["pin13", "SHELL1", "EH1"]}
			pcbX={-4.32}
			pcbY={1.575}
			shape="pill"
			outerWidth={1.0}
			outerHeight={2.1}
			holeWidth={0.6}
			holeHeight={1.7}
		/>
		<platedhole
			portHints={["pin14", "SHELL2", "EH2"]}
			pcbX={4.32}
			pcbY={1.575}
			shape="pill"
			outerWidth={1.0}
			outerHeight={2.1}
			holeWidth={0.6}
			holeHeight={1.7}
		/>
		<platedhole
			portHints={["pin15", "SHELL3", "EH3"]}
			pcbX={-4.32}
			pcbY={-2.625}
			shape="pill"
			outerWidth={1.0}
			outerHeight={1.8}
			holeWidth={0.6}
			holeHeight={1.4}
		/>
		<platedhole
			portHints={["pin16", "SHELL4", "EH4"]}
			pcbX={4.32}
			pcbY={-2.625}
			shape="pill"
			outerWidth={1.0}
			outerHeight={1.8}
			holeWidth={0.6}
			holeHeight={1.4}
		/>

		{/* Plastic locating pegs: NPTH, not free-standing board cutouts. */}
		<hole name="LOC1" pcbX={-2.89} pcbY={1.055} diameter={0.65} />
		<hole name="LOC2" pcbX={2.89} pcbY={1.055} diameter={0.65} />

		<silkscreenpath
			route={[
				{ x: -4.5, y: -1.65 },
				{ x: -4.5, y: 0.35 },
			]}
			strokeWidth={0.15}
		/>
		<silkscreenpath
			route={[
				{ x: 4.5, y: -1.65 },
				{ x: 4.5, y: 0.35 },
			]}
			strokeWidth={0.15}
		/>
		<silkscreenpath
			route={[
				{ x: -4.5, y: -5.225 },
				{ x: 4.5, y: -5.225 },
			]}
			strokeWidth={0.15}
		/>
		<courtyardoutline
			outline={[
				{ x: -4.8, y: 2.95 },
				{ x: 4.8, y: 2.95 },
				{ x: 4.8, y: -5.5 },
				{ x: -4.8, y: -5.5 },
				{ x: -4.8, y: 2.95 },
			]}
		/>
	</footprint>
);

export const UsbDevicePort = () => (
	<>
		{/*
		 * USB4105-GF-A is a 16-contact, USB 2.0 Type-C receptacle. The builtin
		 * usb_c standard preserves separate CC1/CC2 and both plug orientations.
		 * PRODUCTION GATE: verify the selected 0.95 mm shell-stake suffix, local
		 * footprint and enclosure against the current GCT product drawing.
		 */}
		<connector
			name="J201"
			standard="usb_c"
			manufacturerPartNumber="USB4105-GF-A"
			datasheetUrl="https://gct.co/files/drawings/usb4105.pdf"
			pinLabels={{
				pin13: ["SHELL1", "EH1"],
				pin14: ["SHELL2", "EH2"],
				pin15: ["SHELL3", "EH3"],
				pin16: ["SHELL4", "EH4"],
				pin17: ["GND1", "A1B12"],
				pin18: ["VBUS1", "A4B9"],
				pin19: ["SBU2", "B8"],
				pin20: ["CC1", "A5"],
				pin21: ["DM2", "B7", "Dn2"],
				pin22: ["DP1", "A6", "Dp1"],
				pin23: ["DM1", "A7", "Dn1"],
				pin24: ["DP2", "B6", "Dp2"],
				pin25: ["SBU1", "A8"],
				pin26: ["CC2", "B5"],
				pin27: ["VBUS2", "B4A9"],
				pin28: ["GND2", "B1A12"],
			}}
			noConnect={["SBU1", "SBU2"]}
			footprint={<Usb4105Footprint />}
			cadModel={{
				objUrl:
					"https://modules.easyeda.com/3dmodel/4ee8413127e64716b804db03d4b340ae",
				stepUrl:
					"https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/4ee8413127e64716b804db03d4b340ae",
				modelOriginPosition: { x: -0.0000127, y: 1.57499705, z: -1.6800018 },
				size: { x: 8.74997, y: 5.3500529, z: 7.57998484 },
			}}
			allowOffBoard
			pcbX={56.5}
			// 44.775 + 5.225 = +50.000 mm: connector mouth meets the top PCB edge.
			pcbY={44.775}
			pcbRotation={180}
			schX={34}
			schY={0}
			schSectionName="USB"
		/>

		<UsbDataEsd />

		{/* ESP32-S3 USB series damping; place these at the module-side pins. */}
		<resistor
			name="R201"
			resistance="22ohm"
			footprint="0402"
			pcbX={55}
			pcbY={31}
			schX={24.5}
			schY={0.6}
			schSectionName="USB"
		/>
		<resistor
			name="R202"
			resistance="22ohm"
			footprint="0402"
			pcbX={55}
			pcbY={29.5}
			schX={24.5}
			schY={-0.6}
			schSectionName="USB"
		/>

		{/* USB Type-C upstream-facing-port pull-downs; CC pins stay independent. */}
		<resistor
			name="R203"
			resistance="5.1kohm"
			footprint="0603"
			pcbX={49}
			pcbY={39}
			schX={32}
			schY={-2.1}
			schSectionName="USB"
		/>
		<resistor
			name="R204"
			resistance="5.1kohm"
			footprint="0603"
			pcbX={53}
			pcbY={39}
			schX={34}
			schY={-2.1}
			schSectionName="USB"
		/>

		{/*
		 * Self-powered VBUS monitor. VBUS drives only Q201's insulated gate through
		 * R207; R206 discharges the gate when the cable is removed. Q201 then pulls
		 * the controller-powered sense input low. This avoids injecting current
		 * through an unpowered ESP32 GPIO when USB is the only applied source.
		 */}
		<chip
			name="Q201"
			manufacturerPartNumber="BSS138BK,215"
			footprint="sot23"
			pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }}
			pcbX={64}
			pcbY={35}
			schX={29}
			schY={3.1}
			schSectionName="USB"
		/>
		<resistor
			name="R205"
			resistance="10kohm"
			footprint="0603"
			pcbX={60}
			pcbY={36}
			schX={31}
			schY={2}
			schSectionName="USB"
		/>
		<resistor
			name="R206"
			resistance="1Mohm"
			footprint="0603"
			pcbX={64}
			pcbY={39}
			schX={32}
			schY={4.2}
			schSectionName="USB"
		/>
		<resistor
			name="R207"
			resistance="100kohm"
			footprint="0603"
			pcbX={60}
			pcbY={39}
			schX={28}
			schY={4.2}
			schSectionName="USB"
		/>
		<capacitor
			name="C201"
			capacitance="1nF"
			maxVoltageRating="16V"
			footprint="0603"
			pcbX={56.5}
			pcbY={36.5}
			schX={33}
			schY={2}
			schSectionName="USB"
		/>

		{/* Both reversible data contacts join before the connector-side ESD. */}
		<trace from=".J201 > .DP1" to=".U201 > .pin1" />
		<trace from=".J201 > .DP2" to=".U201 > .pin1" />
		<trace from=".J201 > .DM1" to=".U201 > .pin2" />
		<trace from=".J201 > .DM2" to=".U201 > .pin2" />
		<trace from=".U201 > .pin1" to=".R201 > .pin1" />
		<trace from=".U201 > .pin2" to=".R202 > .pin1" />
		<trace from=".R201 > .pin2" to="net.USB_DP_MCU" />
		<trace from=".R202 > .pin2" to="net.USB_DN_MCU" />
		<trace from=".U201 > .pin3" to="net.GND_CTRL" />

		<trace from=".J201 > .CC1" to=".R203 > .pin1" />
		<trace from=".R203 > .pin2" to="net.GND_CTRL" />
		<trace from=".J201 > .CC2" to=".R204 > .pin1" />
		<trace from=".R204 > .pin2" to="net.GND_CTRL" />

		{/* VBUS is sensing-only: it reaches only the high-impedance gate network. */}
		<trace from=".J201 > .VBUS1" to=".R207 > .pin1" />
		<trace from=".J201 > .VBUS2" to=".R207 > .pin1" />
		<trace from=".R207 > .pin2" to="net.USB_VBUS_GATE" />
		<trace from=".R206 > .pin1" to="net.USB_VBUS_GATE" />
		<trace from=".R206 > .pin2" to="net.GND_CTRL" />
		<trace from=".Q201 > .pin1" to="net.USB_VBUS_GATE" />
		<trace from=".Q201 > .pin2" to="net.GND_CTRL" />
		<trace from=".Q201 > .pin3" to="net.USB_VBUS_PRESENT_N" />
		<trace from=".R205 > .pin1" to="net.V3V3_MAIN" />
		<trace from=".R205 > .pin2" to="net.USB_VBUS_PRESENT_N" />
		<trace from=".C201 > .pin1" to="net.USB_VBUS_PRESENT_N" />
		<trace from=".C201 > .pin2" to="net.GND_CTRL" />

		<trace from=".J201 > .GND1" to="net.GND_CTRL" />
		<trace from=".J201 > .GND2" to="net.GND_CTRL" />

		{/*
		 * Rev A has no conductive chassis domain. Bond all receptacle shell tabs
		 * directly to GND_CTRL at the connector with short copper and ground-via
		 * stitching. Revisit this bond if a future metal enclosure adds CHASSIS.
		 */}
		<trace from=".J201 > .SHELL1" to="net.GND_CTRL" />
		<trace from=".J201 > .SHELL2" to="net.GND_CTRL" />
		<trace from=".J201 > .SHELL3" to="net.GND_CTRL" />
		<trace from=".J201 > .SHELL4" to="net.GND_CTRL" />
	</>
);
