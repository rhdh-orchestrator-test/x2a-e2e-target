# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS, self-signed certificates, and virtual hosts
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol validation, SSH root login security check

- **chef-server-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used in the web server configuration - can be preserved as-is or incorporated into Ansible templates

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Evaluate if these components are needed or if they can be replaced with:
  - Ansible Tower/AWX for orchestration
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security roles

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables vulnerable protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to manage SSL configuration with appropriate security settings.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible task to ensure SSH configuration maintains this security setting and add appropriate assertions.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault for private keys

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing functionality currently provided by InSpec.
  - Mitigation: Either keep InSpec as a standalone tool called from Ansible or implement equivalent checks using Ansible's assertion capabilities.

- **Certificate Management**: The current solution generates self-signed certificates.
  - Mitigation: Use Ansible's `openssl_*` modules (already in use) but enhance with better key management practices.

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure with variables

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the website-https role as a security enhancement
   - Add conditional logic to apply based on variables

3. **compliance-testing** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible assertions)
   - Implement equivalent tests in chosen framework

4. **chef-server-deployment** (high complexity)
   - Determine if Chef server is still needed in the new architecture
   - If needed, create Ansible roles to deploy Chef components
   - If not needed, document the removal and any replacement components

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code.
2. The Chef Automate and Chef Infra Server deployment scripts may not be needed in the final Ansible-only solution.
3. The security compliance requirements (TLS configuration, SSH settings) must be maintained in the migrated solution.
4. Test Kitchen is used primarily for development and testing, not for production deployments.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. There are no external dependencies or integrations not visible in the repository.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with proper secret management.