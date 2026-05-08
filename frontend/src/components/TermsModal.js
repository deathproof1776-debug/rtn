import { Shield, WarningCircle, FileText } from '@phosphor-icons/react';

export default function TermsModal({ onClose, onAccept }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80" data-testid="terms-modal">
      <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col animate-fade-in">
        <div className="flex items-center justify-between p-4 border-b border-[var(--bg-surface-active)]">
          <div className="flex items-center gap-2">
            <FileText size={24} className="text-[var(--brand-primary)]" />
            <h3 className="text-lg font-semibold text-[var(--text-primary)]">Community Guidelines & Terms</h3>
          </div>
          <button
            onClick={onClose}
            className="text-[var(--text-muted)] hover:text-[var(--text-primary)] text-2xl leading-none"
            data-testid="close-terms-modal"
          >×</button>
        </div>

        <div className="p-6 overflow-y-auto flex-1 space-y-6 text-[var(--text-secondary)]">
          <section>
            <h4 className="text-[var(--text-primary)] font-semibold mb-3 flex items-center gap-2">
              <WarningCircle size={20} className="text-[var(--brand-danger)]" />
              Prohibited Activities
            </h4>
            <ul className="space-y-2 text-sm list-disc list-inside">
              <li><span className="text-[var(--brand-danger)] font-semibold">User is responsible for following all applicable laws.</span> You are solely responsible for ensuring that any items you trade, sell, or exchange comply with all local, state, and federal laws. This includes but is not limited to controlled substances, regulated goods, and any items prohibited in your jurisdiction.</li>
              <li><span className="text-[var(--brand-danger)] font-semibold">No weapons trafficking.</span> Trading of firearms, explosives, or other regulated weapons must comply with all applicable laws and regulations.</li>
              <li><span className="text-[var(--brand-danger)] font-semibold">No counterfeit goods.</span> Fake, fraudulent, or misrepresented items are not allowed.</li>
            </ul>
          </section>

          <section>
            <h4 className="text-[var(--text-primary)] font-semibold mb-3 flex items-center gap-2">
              <Shield size={20} className="text-[var(--brand-primary)]" />
              Community Standards
            </h4>
            <ul className="space-y-2 text-sm list-disc list-inside">
              <li><span className="text-[var(--brand-primary)] font-semibold">No harassment.</span> Bullying, intimidation, stalking, or any form of harassment towards other members will not be tolerated.</li>
              <li><span className="text-[var(--brand-primary)] font-semibold">No threats or violence.</span> Any threats of violence, promotion of violence, or incitement to harm others is strictly prohibited and may be reported to authorities.</li>
              <li><span className="text-[var(--brand-primary)] font-semibold">No hate speech.</span> Discrimination, slurs, or hateful content targeting individuals or groups is not allowed.</li>
              <li><span className="text-[var(--brand-primary)] font-semibold">Respect privacy.</span> Do not share other members' personal information without consent.</li>
            </ul>
          </section>

          <section className="bg-[var(--bg-surface-hover)] border border-[var(--bg-surface-active)] p-4">
            <h4 className="text-[var(--text-primary)] font-semibold mb-3">Liability Disclaimer</h4>
            <div className="text-sm space-y-3">
              <p>
                <strong className="text-[var(--text-primary)]">User Responsibility:</strong> You are solely responsible for any and all trade deals, transactions, communications, and interactions you engage in through Rebel Trade Network. This includes verifying the legitimacy of items, the trustworthiness of trading partners, and ensuring compliance with all applicable laws.
              </p>
              <p>
                <strong className="text-[var(--text-primary)]">No Liability:</strong> The creators, operators, and administrators of Rebel Trade Network are NOT liable for any losses, damages, disputes, injuries, or legal consequences arising from trades, transactions, or interactions made through this platform.
              </p>
              <p>
                <strong className="text-[var(--text-primary)]">Trade at Your Own Risk:</strong> All trades are conducted at your own risk. We do not guarantee, verify, or endorse any items, services, or members on this platform.
              </p>
            </div>
          </section>

          <section>
            <h4 className="text-[var(--text-primary)] font-semibold mb-3">Enforcement</h4>
            <p className="text-sm">
              Violations of these guidelines may result in warnings, suspension, or permanent removal from the network. Severe violations may be reported to appropriate law enforcement agencies.
            </p>
          </section>
        </div>

        <div className="p-4 border-t border-[var(--bg-surface-active)] flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2 px-4 border border-[var(--bg-surface-active)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
            data-testid="terms-close-button"
          >Close</button>
          <button
            onClick={onAccept}
            className="flex-1 btn-primary"
            data-testid="terms-accept-button"
          >I Accept</button>
        </div>
      </div>
    </div>
  );
}
