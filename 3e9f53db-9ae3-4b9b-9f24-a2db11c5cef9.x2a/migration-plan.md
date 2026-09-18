# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance testing examples integrated with Ansible playbooks, rather than traditional Chef cookbooks. The migration scope is limited as the infrastructure automation is already implemented in Ansible - the primary task is migrating the InSpec compliance tests to native Ansible testing approaches. This is a low-complexity migration with an estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that demonstrate compliance automation integration:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS website deployment with SSL/TLS security compliance testing using InSpec
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec testing
- Key Features: Self-signed SSL certificate generation, Apache virtual host configuration, POODLE vulnerability mitigation, SSL protocol compliance verification

**ssh-security-compliance**:
- Description: SSH security hardening compliance test ensuring root login is disabled per STIG requirements
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance (RHEL-08-000227), SSH configuration validation, security control SRG-OS-000112

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS setup with SSL certificate management
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disables SSLv3, enables TLSv1.2)
- `index.html`: Static test content for website verification
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts)
- **Test Kitchen**: Replace with molecule for Ansible testing framework
- **Vagrant**: Continue using Vagrant or migrate to container-based testing

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates with OpenSSL modules - maintain same approach in Ansible
- SSH hardening compliance: Migrate InSpec controls to Ansible assert tasks with sshd_config validation
- STIG compliance verification: Replace InSpec STIG controls with Ansible security role validation tasks
- No hardcoded credentials detected in the reviewed files - security posture is good

### Technical Challenges
- InSpec control migration: Converting structured InSpec compliance tests to Ansible assert tasks requires careful mapping of test logic
- Test Kitchen replacement: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and verification approaches
- Compliance reporting: InSpec provides structured compliance reporting that needs equivalent implementation in Ansible testing

### Migration Order
1. **website-https-compliance** (low risk, already uses Ansible for provisioning)
2. **ssh-security-compliance** (moderate complexity, requires STIG control mapping)
3. **Infrastructure automation scripts** (low priority, deployment tooling)

### Assumptions
- The repository serves as a demonstration/example rather than production infrastructure code
- Current Ansible playbooks are already functional and don't require significant modification
- InSpec tests are the primary migration target, not the Ansible automation itself
- Test Kitchen integration can be replaced with Molecule without loss of functionality
- SSH and SSL compliance requirements will remain consistent with current STIG standards
- The target environment will continue to use Ubuntu/Debian-based systems as indicated by apt package management
- Self-signed certificates are acceptable for the demonstration use case (production would require proper CA-signed certificates)