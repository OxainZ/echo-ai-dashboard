// Repositories/PolygonSetupRepository.swift
// Echo Copilot — Live price/RVOL/spread enrichment via Polygon.io REST API.
// Wraps any SetupRepositoryProtocol; enriches setups on refresh().
//
// Setup:
//   1. Get a free API key at https://polygon.io
//   2. Enter it in Settings → Data Source → Polygon API Key
//   3. Pull-to-refresh on the Radar tab to enrich prices live
//
// Data mapped per ticker:
//   price      → day.c  (today's close / last trade)
//   rvol       → day.v / prevDay.v
//   spreadPct  → (ask - bid) / mid * 100
//   timestamp  → now

import Foundation

final class PolygonSetupRepository: SetupRepositoryProtocol {
    private let base: any SetupRepositoryProtocol
    private let apiKey: String
    private let session: URLSession

    /// Minimum seconds between live refreshes (free Polygon tier: 5 req/min).
    private let cooldownSeconds: TimeInterval = 15
    private var lastRefresh: Date? = nil

    init(base: any SetupRepositoryProtocol, apiKey: String, session: URLSession = .shared) {
        self.base = base
        self.apiKey = apiKey
        self.session = session
    }

    // MARK: - Protocol

    func fetchSetups() async throws -> [TickerSetup] {
        return try await base.fetchSetups()
    }

    func refresh() async throws -> [TickerSetup] {
        var setups = try await base.fetchSetups()
        guard !setups.isEmpty, !apiKey.isEmpty else { return setups }

        // Rate-limit: skip network call if refreshed recently
        if let last = lastRefresh, Date().timeIntervalSince(last) < cooldownSeconds {
            return setups
        }

        let symbols = setups.map { $0.symbol }.joined(separator: ",")
        guard let url = URL(string: "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers=\(symbols)&apiKey=\(apiKey)") else {
            return setups
        }

        let data: Data
        do {
            let (d, response) = try await session.data(from: url)
            guard (response as? HTTPURLResponse)?.statusCode == 200 else { return setups }
            data = d
            lastRefresh = Date()
        } catch {
            // Network error — return cached setups rather than crashing
            return setups
        }

        guard let snapshot = try? JSONDecoder().decode(PolygonSnapshotResponse.self, from: data) else {
            return setups
        }

        let tickerMap = Dictionary(uniqueKeysWithValues: snapshot.tickers.map { ($0.ticker, $0) })

        for i in setups.indices {
            guard let info = tickerMap[setups[i].symbol] else { continue }
            setups[i].price = info.day.c
            if let prevVol = info.prevDay?.v, prevVol > 0 {
                setups[i].rvol = info.day.v / prevVol
            }
            if let ask = info.lastQuote?.P, let bid = info.lastQuote?.p, (ask + bid) > 0 {
                setups[i].spreadPct = (ask - bid) / ((ask + bid) / 2.0) * 100.0
            }
            setups[i].timestamp = Date()
            try? await base.save(setups[i])
        }

        return setups
    }

    func save(_ setup: TickerSetup) async throws {
        try await base.save(setup)
    }

    func delete(id: UUID) async throws {
        try await base.delete(id: id)
    }
}

// MARK: - Polygon response models

private struct PolygonSnapshotResponse: Decodable {
    let tickers: [PolygonTicker]
}

private struct PolygonTicker: Decodable {
    let ticker: String
    let day: PolygonDay
    let prevDay: PolygonDay?
    let lastQuote: PolygonQuote?
}

private struct PolygonDay: Decodable {
    let c: Double    // close price
    let v: Double    // volume
    let vw: Double?  // volume-weighted avg price
}

private struct PolygonQuote: Decodable {
    let P: Double    // ask
    let p: Double    // bid
}
