package WorkflowsWriteWithOrganizationApps {
    private import Anima::*;

    requirement workflowsWriteWithOrganizationApps {
        doc /* A workflow that moves a branch, creates a release, syncs a fork or opens a pull request shall do it with an installation token of the organization App named for that capability, made in the job that needs it by the pinned token action with only the permissions the write needs, and never with the workflow's own token, so that the credential that writes is the one the rulesets and the organization can name and restrict; and the names that the workflows read for those Apps shall be checkable before a change reaches main without reading any value. */
        @FitnessFunction { trigger = Trigger::commit; }
        subject tools : Toolchain;
    }

    satisfy workflowsWriteWithOrganizationApps by toolchain;

    verification def test_workflows_write_with_organization_apps_use_app_tokens {
        subject tools : Toolchain;
        objective { verify workflowsWriteWithOrganizationApps; }
    }

    verification def test_workflows_write_with_organization_apps_names_checked_by_name_only {
        subject tools : Toolchain;
        objective { verify workflowsWriteWithOrganizationApps; }
    }
}
