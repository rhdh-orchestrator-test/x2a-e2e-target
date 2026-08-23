# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec compliance profiles and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for continuous compliance validation. The repository also includes scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec profiles to migrate. The complexity is low to moderate, as the existing Ansible playbooks can be largely reused, while the InSpec profiles need to be converted to Ansible-native solutions. Estimated timeline for migration is 1-2 weeks for a single developer.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Simple HTML template for the website

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Convert InSpec tests to Ansible assert modules or Molecule tests
  - For continuous compliance: Consider integrating with AWX/Ansible Tower scheduled jobs

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-compatible CI/CD pipeline (GitHub Actions, GitLab CI, etc.)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve security by:
  - Updating to modern TLS configurations (TLS 1.3 where possible)
  - Using stronger cipher suites
  - Implementing proper certificate management

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Incorporate these checks into Ansible roles
  - Implement SSH hardening as part of the base configuration

- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, email in deployment scripts)

### Technical Challenges

- **InSpec to Ansible Conversion**: Converting InSpec compliance profiles to Ansible requires:
  - Understanding the compliance requirements
  - Implementing equivalent checks using Ansible modules
  - Ensuring idempotency and proper reporting
  - Mitigation: Create custom Ansible modules or use assert/fail modules with appropriate conditions

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated:
  - Mitigation: Integrate with AWX/Tower for reporting or implement custom reporting solutions
  - Consider using callback plugins to format check results

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and update to current Ansible best practices
   - Implement idempotency improvements if needed
   - Add tags for selective execution

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Moderate complexity
   - Convert to Ansible roles for Chef server deployment
   - Implement proper secret management with Ansible Vault
   - Add validation and error handling

3. **InSpec Profiles** (website_https_verify.rb, ssh_profile.rb): High complexity
   - Convert to Ansible assertion tasks or custom modules
   - Implement reporting mechanism
   - Integrate with CI/CD pipeline

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance validation
2. The existing Ansible playbooks are functional and follow reasonable practices
3. There is no requirement to maintain backward compatibility with Chef Automate or Chef Server
4. The deployment scripts are used for setting up test environments and not production systems
5. The hardcoded credentials in the deployment scripts are not used in production environments
6. The self-signed certificates are only used for testing purposes
7. The compliance profiles are based on industry standards that need to be maintained in the Ansible implementation