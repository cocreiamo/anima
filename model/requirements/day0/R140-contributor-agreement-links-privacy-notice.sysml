package R140 {
    private import Anima::*;

    requirement <'R140'> contributorAgreementLinksPrivacyNotice {
        doc /* The contributor agreement and the contributing guide shall link a privacy notice that exists in the repository. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    verification def test_R140_contributor_agreement_links_privacy_notice {
        subject tools : Toolchain;
        objective { verify contributorAgreementLinksPrivacyNotice; }
    }
}
