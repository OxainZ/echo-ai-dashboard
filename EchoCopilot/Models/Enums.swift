// Models/Enums.swift
// Echo Copilot — All domain enumerations

import Foundation

// MARK: - SetupStatus

enum SetupStatus: String, Codable, CaseIterable {
    case actionable = "Actionable"
    case shadow = "Shadow"
}

// MARK: - TradingLane

enum TradingLane: String, Codable, CaseIterable {
    case main = "Main"
    case micro = "Micro"
}

// MARK: - CashCompliance

enum CashCompliance: String, Codable, CaseIterable {
    case cashOK = "Cash OK"
    case waitTPlus1 = "Wait T+1"
}

// MARK: - ShadowReason

enum ShadowReason: Codable, Hashable, CustomStringConvertible {
    case missingTrigger
    case missingInvalidation
    case missingPrice
    case spreadTooWide
    case rvolTooLow
    case volZTooLow
    case halted
    case ssrRestriction
    case impactTooHigh
    case missingVerification
    case missingTargets
    case other(String)

    var description: String {
        switch self {
        case .missingTrigger:       return "Missing trigger"
        case .missingInvalidation:  return "Missing invalidation"
        case .missingPrice:         return "Missing price"
        case .spreadTooWide:        return "Spread too wide"
        case .rvolTooLow:           return "RVOL too low"
        case .volZTooLow:           return "Vol-Z too low"
        case .halted:               return "Halted"
        case .ssrRestriction:       return "SSR restriction"
        case .impactTooHigh:        return "Impact % too high"
        case .missingVerification:  return "Unverified setup"
        case .missingTargets:       return "Missing targets"
        case .other(let msg):       return msg
        }
    }

    // MARK: Codable support for associated value

    private enum CodingKeys: String, CodingKey { case type, value }

    func encode(to encoder: Encoder) throws {
        var c = encoder.container(keyedBy: CodingKeys.self)
        switch self {
        case .missingTrigger:      try c.encode("missingTrigger", forKey: .type)
        case .missingInvalidation: try c.encode("missingInvalidation", forKey: .type)
        case .missingPrice:        try c.encode("missingPrice", forKey: .type)
        case .spreadTooWide:       try c.encode("spreadTooWide", forKey: .type)
        case .rvolTooLow:          try c.encode("rvolTooLow", forKey: .type)
        case .volZTooLow:          try c.encode("volZTooLow", forKey: .type)
        case .halted:              try c.encode("halted", forKey: .type)
        case .ssrRestriction:      try c.encode("ssrRestriction", forKey: .type)
        case .impactTooHigh:       try c.encode("impactTooHigh", forKey: .type)
        case .missingVerification: try c.encode("missingVerification", forKey: .type)
        case .missingTargets:      try c.encode("missingTargets", forKey: .type)
        case .other(let v):
            try c.encode("other", forKey: .type)
            try c.encode(v, forKey: .value)
        }
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        let type = try c.decode(String.self, forKey: .type)
        switch type {
        case "missingTrigger":      self = .missingTrigger
        case "missingInvalidation": self = .missingInvalidation
        case "missingPrice":        self = .missingPrice
        case "spreadTooWide":       self = .spreadTooWide
        case "rvolTooLow":          self = .rvolTooLow
        case "volZTooLow":          self = .volZTooLow
        case "halted":              self = .halted
        case "ssrRestriction":      self = .ssrRestriction
        case "impactTooHigh":       self = .impactTooHigh
        case "missingVerification": self = .missingVerification
        case "missingTargets":      self = .missingTargets
        default:
            let value = try c.decodeIfPresent(String.self, forKey: .value) ?? type
            self = .other(value)
        }
    }
}

// MARK: - SortOption

enum SortOption: String, Codable, CaseIterable, Identifiable {
    case newest          = "Newest"
    case highestRVOL     = "Highest RVOL"
    case lowestSpread    = "Lowest Spread"
    case actionableFirst = "Actionable First"

    var id: String { rawValue }
}

// MARK: - RadarFilter

enum RadarFilter: String, CaseIterable, Identifiable {
    case all        = "All"
    case actionable = "Actionable"
    case shadow     = "Shadow"
    case main       = "Main"
    case micro      = "Micro"

    var id: String { rawValue }
}
