// Components/StatusBadgeView.swift
// Echo Copilot — Actionable / Shadow colored badge

import SwiftUI

struct StatusBadgeView: View {
    let status: SetupStatus

    var body: some View {
        Text(status.rawValue.uppercased())
            .font(.system(size: 10, weight: .bold, design: .monospaced))
            .foregroundStyle(textColor)
            .padding(.horizontal, 7)
            .padding(.vertical, 3)
            .background(backgroundColor, in: Capsule())
    }

    private var textColor: Color {
        status == .actionable ? .black : .white
    }

    private var backgroundColor: Color {
        status == .actionable ? Color.green : Color.orange.opacity(0.8)
    }
}

#Preview {
    HStack {
        StatusBadgeView(status: .actionable)
        StatusBadgeView(status: .shadow)
    }
    .padding()
    .background(.black)
}
