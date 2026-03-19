// Components/MetricRowView.swift
// Echo Copilot — Label + value row for setup metrics

import SwiftUI

struct MetricRowView: View {
    let label: String
    let value: String
    var highlight: Bool = false
    var valueColor: Color = .primary

    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .font(.subheadline.monospacedDigit())
                .fontWeight(highlight ? .semibold : .regular)
                .foregroundStyle(highlight ? valueColor : .primary)
        }
    }
}

#Preview {
    VStack {
        MetricRowView(label: "Trigger", value: "491.10", highlight: true, valueColor: .green)
        MetricRowView(label: "Spread", value: "0.18%")
        MetricRowView(label: "RVOL", value: "2.8x", highlight: true, valueColor: .cyan)
    }
    .padding()
    .background(.black)
}
