// Models/TickerSetup.swift
// Echo Copilot — Core setup model representing a single trade candidate

import Foundation

struct TickerSetup: Identifiable, Codable, Hashable {
    var id: UUID
    var symbol: String
    var companyName: String?
    var lane: TradingLane
    var status: SetupStatus
    var price: Double?
    var priorClose: Double?
    var pmh: Double           // Pre-market high
    var pdh: Double           // Prior day high
    var pdl: Double?          // Prior day low
    var trigger: Double?
    var invalidation: Double?
    var target1: Double?
    var target2: Double?
    var spreadPct: Double?    // Bid-ask spread as percent
    var rvol: Double?         // Relative volume
    var volZ: Double?         // Volume Z-score
    var dollarVolume: Double? // Today's dollar volume
    var adtvDollar: Double?   // Average daily dollar volume
    var impactPctADTV: Double? // Position impact as % of ADTV
    var halted: Bool
    var ssrActive: Bool
    var cashCompliance: CashCompliance
    var timestamp: Date
    var notes: String
    var catalystSummary: String?
    var shadowReasons: [ShadowReason]
    var isVerified: Bool

    init(
        id: UUID = UUID(),
        symbol: String,
        companyName: String? = nil,
        lane: TradingLane = .main,
        status: SetupStatus = .shadow,
        price: Double? = nil,
        priorClose: Double? = nil,
        pmh: Double,
        pdh: Double,
        pdl: Double? = nil,
        trigger: Double? = nil,
        invalidation: Double? = nil,
        target1: Double? = nil,
        target2: Double? = nil,
        spreadPct: Double? = nil,
        rvol: Double? = nil,
        volZ: Double? = nil,
        dollarVolume: Double? = nil,
        adtvDollar: Double? = nil,
        impactPctADTV: Double? = nil,
        halted: Bool = false,
        ssrActive: Bool = false,
        cashCompliance: CashCompliance = .cashOK,
        timestamp: Date = Date(),
        notes: String = "",
        catalystSummary: String? = nil,
        shadowReasons: [ShadowReason] = [],
        isVerified: Bool = false
    ) {
        self.id = id
        self.symbol = symbol
        self.companyName = companyName
        self.lane = lane
        self.status = status
        self.price = price
        self.priorClose = priorClose
        self.pmh = pmh
        self.pdh = pdh
        self.pdl = pdl
        self.trigger = trigger
        self.invalidation = invalidation
        self.target1 = target1
        self.target2 = target2
        self.spreadPct = spreadPct
        self.rvol = rvol
        self.volZ = volZ
        self.dollarVolume = dollarVolume
        self.adtvDollar = adtvDollar
        self.impactPctADTV = impactPctADTV
        self.halted = halted
        self.ssrActive = ssrActive
        self.cashCompliance = cashCompliance
        self.timestamp = timestamp
        self.notes = notes
        self.catalystSummary = catalystSummary
        self.shadowReasons = shadowReasons
        self.isVerified = isVerified
    }
}
