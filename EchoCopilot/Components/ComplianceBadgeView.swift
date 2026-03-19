// Components/ComplianceBadgeView.swift
// Echo Copilot — Cash OK / Wait T+1 badge

import SwiftUI

struct ComplianceBadgeView: View {
    let compliance: CashCompliance

    var body: some View {
        HStack(spacing: 3) {
            Image(systemName: iconName)
                .font(.system(size: 9, weight: .bold))
            Text(compliance.rawValue.uppercased())
                .font(.system(size: 9, weight: .bold, design: .monospaced))
        }
        .foregroundStyle(textColor)
        .padding(.horizontal, 7)
        .padding(.vertical, 3)
        .background(backgroundColor, in: Capsule())
    }

    private var iconName: String {
        compliance == .cashOK ? "checkmark.circle.fill" : "clock.fill"
    }

    private var textColor: Color {
        compliance == .cashOK ? .black : .white
    }

    private var backgroundColor: Color {
        compliance == .cashOK ? Color.mint : Color.purple.opacity(0.8)
    }
}

#Preview {
    VStack {
        ComplianceBadgeView(compliance: .cashOK)
        ComplianceBadgeView(compliance: .waitTPlus1)
    }
    .padding()
    .background(.black)
}
