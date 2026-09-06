"""
seed_demo_cases.py

Seeds one prior "victim case" into the case store using the SAME mock
address-derivation logic as walletrace/tools/mocks.py, so that when you
live-trace a DIFFERENT wallet ending in the same 6 characters during the
demo, cross-case correlation finds a genuine overlap.

Why this works:
mocks.get_cluster(address) derives its co-spend addresses from the LAST
6 CHARACTERS of the input address. So two different wallets — reported
by two different victims — sharing the same suffix resolve to the SAME
downstream cluster addresses. This simulates real deposit-address reuse
across victims, which is exactly what the correlation feature catches.

Usage:
    python seed_demo_cases.py

Then, during the live demo, trace any wallet ending in the same suffix
used below and related_cases should populate.
"""

from walletrace.case_store import init_db, save_case
from walletrace.tools.mocks import get_cluster

# Pick the shared suffix your live demo wallet will also end with
DEMO_SUFFIX = "9F2E1D"
PRIOR_VICTIM_WALLET = f"0xABCDEF1234567890ABCDEF1234567890AB{DEMO_SUFFIX}"
PRIOR_CASE_ID = "CASE-2026-04521"
PRIOR_CASE_EXCHANGE = "MockEx India"


def main():
    init_db()

    # Run the SAME clustering logic the live pipeline uses, so stored
    # addresses are exactly what get_cluster() would produce for this wallet.
    cluster = get_cluster(PRIOR_VICTIM_WALLET)

    save_case(
        case_id=PRIOR_CASE_ID,
        addresses=cluster["addresses"],
        exchange=PRIOR_CASE_EXCHANGE,
    )

    print(f"Seeded {PRIOR_CASE_ID}")
    print(f"  Wallet:    {PRIOR_VICTIM_WALLET}")
    print(f"  Cluster:   {cluster['cluster_id']}")
    print(f"  Addresses: {cluster['addresses']}")
    print()
    print("Now trace any wallet ending in the same suffix live in your demo, e.g.:")
    print(f"  TVictimTwoReportedWallet00{DEMO_SUFFIX}")
    print("...related_cases should show overlap with CASE-2026-04521.")


if __name__ == "__main__":
    main()