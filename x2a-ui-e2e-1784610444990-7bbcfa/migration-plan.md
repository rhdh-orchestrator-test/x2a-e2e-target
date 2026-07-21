# MIGRATION FROM MIXED CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks, Chef InSpec tests, and Chef Automate/Infra Server deployment scripts. The migration scope is relatively small, with only a few components requiring conversion. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which are already in Ansible format) and medium complexity for converting the InSpec tests to Ansible testing frameworks.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

No traditional modules (Chef cookbooks, Puppet modules, or PowerShell modules) were found in this repository. Instead, the repository contains:

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS, creates self-signed certificates, and deploys a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening for Apache SSL configuration

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant VM
- `index.html`: Simple HTML file used as a template for the website deployment
- `tests/website_https_verify.rb`: Chef InSpec test to verify HTTPS configuration and website availability
- `tests/ssh_profile.rb`: Chef InSpec test to verify SSH security configuration (root login disabled)

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Convert InSpec tests to equivalent Ansible tasks with register/assert pattern

- **Test Kitchen (latest)**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Keep Test Kitchen but use the ansible_playbook provisioner (already in use)

- **Vagrant (latest)**: Can be retained as the VM provider for testing

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for web UI and job scheduling
  - Option 2: GitLab CI/CD or Jenkins for pipeline execution
  - Option 3: Simple Git repository with CI/CD integration

### Security Considerations

- **SSL Configuration**: The `poodle_fix.yml` playbook addresses the POODLE vulnerability by enforcing TLSv1.2. This security hardening should be preserved in the migrated solution.

- **SSH Hardening**: The `ssh_profile.rb` InSpec test verifies that root login via SSH is disabled. This security check should be converted to an equivalent Ansible test.

- **Self-signed Certificates**: The `website_https.yml` playbook generates self-signed certificates. In production, consider using Let's Encrypt or another trusted CA.

- **Vault/secrets management**: 
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets identified (user credentials in both deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks may require additional logic and different assertion patterns.
  - Mitigation: Use Ansible's assert module with appropriate conditions or consider using Molecule for testing.

- **Chef Automate/Infra Server Replacement**: Determining the right Ansible-based alternative for Chef Automate's functionality.
  - Mitigation: Evaluate AWX/Tower, GitLab CI/CD, or Jenkins based on specific requirements.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format. Only need to review and potentially optimize.

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Medium complexity, convert to Ansible testing framework.

3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, replace with Ansible roles for deploying alternative infrastructure.

### Assumptions

1. The repository appears to be primarily educational/demonstrative rather than production code, based on the simple "Hello World" website and self-signed certificates.

2. The target environment is Ubuntu 20.04 using Vagrant for virtualization, but the actual deployment environment is not clearly specified.

3. The Chef Automate and Chef Infra Server deployment scripts are intended for on-premises or cloud VMs, but specific cloud provider details are not provided.

4. The security requirements (POODLE mitigation, SSH hardening) are important and should be preserved in the migrated solution.

5. The repository does not contain traditional Chef cookbooks or recipes, only Ansible playbooks and Chef InSpec tests.

6. The migration will need to address both the infrastructure-as-code components (Ansible playbooks) and the testing framework (InSpec tests).