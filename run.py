import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
import sys

# choices
allowed_compression = ["none","deflate","gzip"]
allowed_devices = ["auto","cpu","gpu"]

options = VarParsing()
options.register("config", "step2_PAT", VarParsing.multiplicity.singleton, VarParsing.varType.string, "cmsDriver-generated config to import")
options.register("maxEvents", -1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Number of events to process (-1 for all)")
options.register("sonic", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "enable SONIC in workflow")
options.register("serverName", "default", VarParsing.multiplicity.singleton, VarParsing.varType.string, "name for server (used internally)")
options.register("address", "hammer-f014.rcac.purdue.edu", VarParsing.multiplicity.singleton, VarParsing.varType.string, "server address")
options.register("port", 8021, VarParsing.multiplicity.singleton, VarParsing.varType.int, "server port")
options.register("params", "", VarParsing.multiplicity.singleton, VarParsing.varType.string, "json file containing server address/port")
options.register("threads", 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "number of threads")
options.register("streams", 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "number of streams")
options.register("verbose", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "enable verbose output")
options.register("shm", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "enable shared memory")
options.register("compression", "", VarParsing.multiplicity.singleton, VarParsing.varType.string, "enable I/O compression (choices: {})".format(', '.join(allowed_compression)))
options.register("ssl", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "enable SSL authentication for server communication")
options.register("device","auto", VarParsing.multiplicity.singleton, VarParsing.varType.string, "specify device for fallback server (choices: {})".format(', '.join(allowed_devices)))
options.register("docker", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "use Docker for fallback server")
options.register("tmi", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "include time/memory summary")
options.register("dump", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "dump process python config")
options.register("outputName", "step4.root", VarParsing.multiplicity.singleton, VarParsing.varType.string, "name for the output MiniAOD file")
options.register("jsonName", "result_sonic.json", VarParsing.multiplicity.singleton, VarParsing.varType.string, "output json name for timing")
options.parseArguments()

if len(options.params)>0:
    with open(options.params,'r') as pfile:
        pdict = json.load(pfile)
    options.address = pdict["address"]
    options.port = int(pdict["port"])
    print("server = "+options.address+":"+str(options.port))

# check compression
if len(options.compression)>0 and options.compression not in allowed_compression:
    raise ValueError("Unknown compression setting: {}".format(options.compression))

# check devices
options.device = options.device.lower()
if options.device not in allowed_devices:
    raise ValueError("Unknown device: {}".format(options.device))

from Configuration.ProcessModifiers.allSonicTriton_cff import allSonicTriton
# need to do this before process is created/imported
if options.sonic:
    allSonicTriton._setChosen()

process = getattr(__import__(options.config,fromlist=["process"]),"process")
if options.sonic:
    process._Process__modifiers = process._Process__modifiers + (allSonicTriton,)

if options.threads>0:
    process.options.numberOfThreads = options.threads
    process.options.numberOfStreams = options.streams

process.maxEvents.input = cms.untracked.int32(options.maxEvents)

process.MINIAODSIMoutput.fileName = cms.untracked.string(options.outputName)

if options.sonic:
    process.TritonService.verbose = options.verbose
    process.TritonService.fallback.verbose = options.verbose
    process.TritonService.fallback.useDocker = options.docker
    if options.device != "auto":
        process.TritonService.fallback.useGPU = options.device=="gpu"
    if len(options.address)>0:
        process.TritonService.servers.append(
            cms.PSet(
                name = cms.untracked.string(options.serverName),
                address = cms.untracked.string(options.address),
                port = cms.untracked.uint32(options.port),
                useSsl = cms.untracked.bool(options.ssl),
                rootCertificates = cms.untracked.string(""),
                privateKey = cms.untracked.string(""),
                certificateChain = cms.untracked.string(""),
            )
        )

# propagate changes to all SONIC producers
keepMsgs = ['TritonClient','TritonService']
for producer in process._Process__producers.values():
    if hasattr(producer,'Client'):
        if hasattr(producer.Client,'verbose'):
            producer.Client.verbose = options.verbose
            keepMsgs.extend([producer._TypedParameterizable__type,producer._TypedParameterizable__type+":TritonClient"])
        if hasattr(producer.Client,'compression'):
            producer.Client.compression = options.compression
        if hasattr(producer.Client,'useSharedMemory'):
            producer.Client.useSharedMemory = options.shm

if options.verbose:
    process.load('FWCore/MessageService/MessageLogger_cfi')
    process.MessageLogger.cerr.FwkReport.reportEvery = 500
    for msg in keepMsgs:
        setattr(process.MessageLogger.cerr,msg,
            cms.untracked.PSet(
                limit = cms.untracked.int32(10000000),
            )
        )

if options.tmi:
    from Validation.Performance.TimeMemorySummary import customise
    process = customise(process)

if options.dump:
    print(process.dumpPython())
    sys.exit(0)

process.FastTimerService = cms.Service( "FastTimerService",
    dqmPath = cms.untracked.string( "DQM/TimerService" ),
    dqmModuleTimeRange = cms.untracked.double( 40.0 ),
    enableDQMbyPath = cms.untracked.bool( True ),
    writeJSONSummary = cms.untracked.bool( True ),
    dqmPathMemoryResolution = cms.untracked.double( 5000.0 ),
    enableDQM = cms.untracked.bool( True ),
    enableDQMbyModule = cms.untracked.bool( True ),
    dqmModuleMemoryRange = cms.untracked.double( 100000.0 ),
    dqmModuleMemoryResolution = cms.untracked.double( 500.0 ),
    dqmMemoryResolution = cms.untracked.double( 5000.0 ),
    enableDQMbyLumiSection = cms.untracked.bool( True ),
    dqmPathTimeResolution = cms.untracked.double( 0.5 ),
    printEventSummary = cms.untracked.bool( False ),
    dqmPathTimeRange = cms.untracked.double( 100.0 ),
    dqmTimeRange = cms.untracked.double( 2000.0 ),
    enableDQMTransitions = cms.untracked.bool( False ),
    dqmPathMemoryRange = cms.untracked.double( 1000000.0 ),
    dqmLumiSectionsRange = cms.untracked.uint32( 2500 ),
    enableDQMbyProcesses = cms.untracked.bool( True ),
    dqmMemoryRange = cms.untracked.double( 1000000.0 ),
    dqmTimeResolution = cms.untracked.double( 5.0 ),
    printRunSummary = cms.untracked.bool( False ),
    dqmModuleTimeResolution = cms.untracked.double( 0.2 ),
    printJobSummary = cms.untracked.bool( True ),
    jsonFileName = cms.untracked.string(  options.jsonName )
)

process.ThroughputService = cms.Service( "ThroughputService",
    dqmPath = cms.untracked.string( "HLT/Throughput" ),
    eventRange = cms.untracked.uint32( 10000 ),
    timeRange = cms.untracked.double( 60000.0 ),
    printEventSummary = cms.untracked.bool( True ),
    eventResolution = cms.untracked.uint32( 100 ),
    enableDQM = cms.untracked.bool( True ),
    dqmPathByProcesses = cms.untracked.bool( True ),
    timeResolution = cms.untracked.double( 5.828 )
)

process.load('FWCore.MessageLogger.MessageLogger_cfi')
if process.maxEvents.input.value()>10:
     process.MessageLogger.cerr.FwkReport.reportEvery = process.maxEvents.input.value()//10
if process.maxEvents.input.value()>2000 or process.maxEvents.input.value()<0:
     process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.cerr.ThroughputService = cms.untracked.PSet(
    limit = cms.untracked.int32(10000000),
    reportEvery = cms.untracked.int32(1)
)
