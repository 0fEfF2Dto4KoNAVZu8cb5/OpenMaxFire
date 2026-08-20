# BixCheck replacement feature map

OpenMaxFire's Linux tool should ultimately aim to replace essentially all useful BixCheck functionality while keeping dangerous service operations explicit.

## Communication and identity

- serial-port discovery/open/close
- stove communication health
- stove/model identification
- firmware/software version identification
- internal/calculated checksum and data-format verification
- serial number / production / model individualization readback

## Runtime operation

- live telemetry
- stove ON/OFF
- heat-level UP/DOWN / target level
- fuel selection and hardware configuration where supported
- blocked-flue and lean-burn monitoring
- thermostat / automatic-restart-related settings where supported
- trim-pot / control modes where supported

## Calibration/configuration

- full configuration readback
- individual parameter read/write
- fuel A / fuel B calibration data
- fan speed adjustments
- feed-rate adjustments
- ash-content adjustments
- startup / ash-dump adjustments
- individualization/calculation workflow
- formatting / initialization workflow
- checksum/data-protection validation
- calibration wizard or guided equivalent

## Logging and diagnostics

- selectable telemetry logging
- long-term data logs
- raw/debug serial communication tools
- reproducible diagnostic captures

## Factory checkout / tests

Target parity includes tests for components exposed by BixCheck/service protocol, including:

- fans
- igniters
- feed mechanism
- ash drive/dump
- air pump
- control panel / switches
- thermocouple
- thermostat
- fuel switch
- other interactive and automatic checkout tests discovered in software/protocol analysis

## Firmware service

- identify installed firmware
- preserve embedded/external firmware images
- bootloader/downloader communication
- firmware loading/flashing
- interrupted-download recovery behavior
- post-flash calibration / configuration handling

## Documentation

- in-tool help and command descriptions
- protocol/register reference
- warnings around dangerous service functions
