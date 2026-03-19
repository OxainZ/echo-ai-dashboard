// Components/LaneBadgeView.swift
// Echo Copilot — Main / Micro lane badge

import SwiftUI

struct LaneBadgeView: View {
    let lane: TradingLane

    var body: some View {
        Text(lane.rawValue.uppercased())
            .font(.system(size: 10, weight: .semibold, design: .monospaced))
            .foregroundStyle(textColor)
            .padding(.horizontal, 7)
            .padding(.vertical, 3)
            .background(backgroundColor, in: Capsule())
    }

    private var textColor: Color {
        lane == .main ? .white : .black
    }

    private var backgroundColor: Color {
        lane == .main ? Color.blue : Color.yellow
    }
}

#Preview {
    HStack {
        LaneBadgeView(lane: .main)
        LaneBadgeView(lane: .micro)
    }
    .padding()
    .background(.black)
}
