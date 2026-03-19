// SampleData/SampleSetups.swift
// Echo Copilot — 8 realistic U.S. equity setups for development and preview

import Foundation

enum SampleSetups {
    static var all: [TickerSetup] { [nvda, aapl, tsla, gme, meta, amzn, msft, rivn] }

    // MARK: 1. NVDA — Actionable, Main Lane, Cash OK

    static let nvda = TickerSetup(
        symbol: "NVDA",
        companyName: "NVIDIA Corporation",
        lane: .main,
        status: .actionable,
        price: 487.50,
        priorClose: 480.20,
        pmh: 491.00,
        pdh: 489.40,
        pdl: 475.10,
        trigger: 491.10,
        invalidation: 475.00,
        target1: 500.00,
        target2: 512.00,
        spreadPct: 0.18,
        rvol: 2.8,
        volZ: 2.1,
        dollarVolume: 4_250_000_000,
        adtvDollar: 2_850_000_000,
        impactPctADTV: 0.12,
        halted: false,
        ssrActive: false,
        cashCompliance: .cashOK,
        timestamp: Date().addingTimeInterval(-300),
        notes: "Strong PM momentum on earnings beat. Clean PMH trigger.",
        catalystSummary: "Q3 earnings beat by $0.40 EPS; raised FY guidance 12%",
        shadowReasons: [],
        isVerified: true
    )

    // MARK: 2. AAPL — Shadow (missing trigger + targets + RVOL/Vol-Z low)

    static let aapl = TickerSetup(
        symbol: "AAPL",
        companyName: "Apple Inc.",
        lane: .main,
        status: .shadow,
        price: 178.30,
        priorClose: 175.20,
        pmh: 179.00,
        pdh: 178.85,
        pdl: 172.10,
        trigger: nil,
        invalidation: 172.00,
        target1: nil,
        target2: nil,
        spreadPct: 0.22,
        rvol: 0.9,
        volZ: 0.4,
        dollarVolume: 1_100_000_000,
        adtvDollar: 2_100_000_000,
        impactPctADTV: nil,
        halted: false,
        ssrActive: false,
        cashCompliance: .cashOK,
        timestamp: Date().addingTimeInterval(-900),
        notes: "Watching for trigger confirmation above PDH",
        catalystSummary: nil,
        shadowReasons: [.missingTrigger, .missingTargets, .rvolTooLow, .volZTooLow],
        isVerified: false
    )

    // MARK: 3. TSLA — Actionable, Main Lane, Wait T+1

    static let tsla = TickerSetup(
        symbol: "TSLA",
        companyName: "Tesla, Inc.",
        lane: .main,
        status: .actionable,
        price: 245.80,
        priorClose: 238.50,
        pmh: 249.00,
        pdh: 247.30,
        pdl: 232.00,
        trigger: 249.10,
        invalidation: 232.00,
        target1: 258.00,
        target2: 268.00,
        spreadPct: 0.28,
        rvol: 1.9,
        volZ: 1.4,
        dollarVolume: 3_800_000_000,
        adtvDollar: 3_200_000_000,
        impactPctADTV: 0.24,
        halted: false,
        ssrActive: false,
        cashCompliance: .waitTPlus1,
        timestamp: Date().addingTimeInterval(-120),
        notes: "T+1 wait — confirm settlement before entering",
        catalystSummary: "Delivery beat + China expansion news",
        shadowReasons: [],
        isVerified: true
    )

    // MARK: 4. GME — Shadow, Micro Lane (spread too wide + RVOL low)

    static let gme = TickerSetup(
        symbol: "GME",
        companyName: "GameStop Corp.",
        lane: .micro,
        status: .shadow,
        price: 14.55,
        priorClose: 13.80,
        pmh: 15.20,
        pdh: 14.75,
        pdl: 13.10,
        trigger: 15.25,
        invalidation: 13.10,
        target1: 16.50,
        target2: 18.00,
        spreadPct: 0.72,   // Exceeds 0.25% micro threshold
        rvol: 1.1,         // Below 1.5 threshold
        volZ: 0.8,         // Below 1.0 threshold
        dollarVolume: 48_000_000,
        adtvDollar: 95_000_000,
        impactPctADTV: nil,
        halted: false,
        ssrActive: true,
        cashCompliance: .cashOK,
        timestamp: Date().addingTimeInterval(-1800),
        notes: "Meme flow elevated but spread and volume quality insufficient",
        catalystSummary: "Social media attention spike",
        shadowReasons: [.spreadTooWide, .rvolTooLow, .volZTooLow, .ssrRestriction],
        isVerified: false
    )

    // MARK: 5. META — Actionable, Micro Lane, Cash OK

    static let meta = TickerSetup(
        symbol: "META",
        companyName: "Meta Platforms, Inc.",
        lane: .micro,
        status: .actionable,
        price: 512.40,
        priorClose: 505.00,
        pmh: 515.00,
        pdh: 513.80,
        pdl: 500.00,
        trigger: 515.10,
        invalidation: 500.00,
        target1: 522.00,
        target2: 530.00,
        spreadPct: 0.19,
        rvol: 2.1,
        volZ: 1.7,
        dollarVolume: 2_100_000_000,
        adtvDollar: 1_400_000_000,
        impactPctADTV: 0.18,
        halted: false,
        ssrActive: false,
        cashCompliance: .cashOK,
        timestamp: Date().addingTimeInterval(-60),
        notes: "Clean trend structure, micro size",
        catalystSummary: "AI product launch drove PM gap",
        shadowReasons: [],
        isVerified: true
    )

    // MARK: 6. AMZN — Shadow, Main Lane (halted)

    static let amzn = TickerSetup(
        symbol: "AMZN",
        companyName: "Amazon.com, Inc.",
        lane: .main,
        status: .shadow,
        price: 182.10,
        priorClose: 185.00,
        pmh: 183.00,
        pdh: 187.50,
        pdl: 180.00,
        trigger: 183.10,
        invalidation: 180.00,
        target1: 187.50,
        target2: 192.00,
        spreadPct: 0.21,
        rvol: 3.1,
        volZ: 2.4,
        dollarVolume: 2_900_000_000,
        adtvDollar: 1_600_000_000,
        impactPctADTV: 0.35,
        halted: true,    // Halted — hard block
        ssrActive: false,
        cashCompliance: .cashOK,
        timestamp: Date().addingTimeInterval(-2400),
        notes: "Halted pending regulatory news — do not trade until cleared",
        catalystSummary: "FTC ruling pending",
        shadowReasons: [.halted],
        isVerified: true
    )

    // MARK: 7. MSFT — Shadow, Main Lane (unverified)

    static let msft = TickerSetup(
        symbol: "MSFT",
        companyName: "Microsoft Corporation",
        lane: .main,
        status: .shadow,
        price: 415.00,
        priorClose: 410.00,
        pmh: 418.00,
        pdh: 416.50,
        pdl: 407.00,
        trigger: 418.10,
        invalidation: 407.00,
        target1: 425.00,
        target2: 432.00,
        spreadPct: 0.14,
        rvol: 1.8,
        volZ: 1.3,
        dollarVolume: 3_100_000_000,
        adtvDollar: 2_200_000_000,
        impactPctADTV: 0.20,
        halted: false,
        ssrActive: false,
        cashCompliance: .cashOK,
        timestamp: Date().addingTimeInterval(-3600),
        notes: "Metrics look good but needs secondary verification",
        catalystSummary: "Copilot+ PC wave announcement",
        shadowReasons: [.missingVerification],
        isVerified: false  // Not yet verified
    )

    // MARK: 8. RIVN — Shadow, Micro Lane (impact too high + Wait T+1)

    static let rivn = TickerSetup(
        symbol: "RIVN",
        companyName: "Rivian Automotive, Inc.",
        lane: .micro,
        status: .shadow,
        price: 12.80,
        priorClose: 11.90,
        pmh: 13.40,
        pdh: 13.10,
        pdl: 11.50,
        trigger: 13.45,
        invalidation: 11.50,
        target1: 14.50,
        target2: 15.80,
        spreadPct: 0.22,
        rvol: 2.4,
        volZ: 1.9,
        dollarVolume: 180_000_000,
        adtvDollar: 320_000_000,
        impactPctADTV: 0.58,  // Exceeds 0.30% micro threshold
        halted: false,
        ssrActive: false,
        cashCompliance: .waitTPlus1,
        timestamp: Date().addingTimeInterval(-600),
        notes: "Good volume but position impact exceeds micro threshold",
        catalystSummary: "Partnership with major OEM announced",
        shadowReasons: [.impactTooHigh],
        isVerified: true
    )
}
