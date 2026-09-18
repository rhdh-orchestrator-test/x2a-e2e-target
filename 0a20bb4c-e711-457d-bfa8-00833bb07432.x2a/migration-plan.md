# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is minimal as the infrastructure automation is already implemented in Ansible - the primary task is replacing Chef InSpec testing with native Ansible testing solutions. Timeline estimate: 1-2 weeks for a small team to implement native Ansible testing and remove Chef dependencies.

## Module Migration Plan

This repository contains Chef InSpec compliance tests integrated with existing Ansible playbooks that need migration to pure Ansible solutions:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS web server deployment with SSL/TLS configuration and compliance verification using Chef InSpec
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec testing
- Key Features: Apache 2.4.41 installation, self-signed SSL certificate generation, virtual host configuration, POODLE vulnerability mitigation (TLS 1.2 enforcement), compliance testing for HTTPS functionality and SSH security

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with Chef InSpec verification - needs replacement with molecule or native Ansible testing
- `website_https.yml`: Complete Ansible playbook for Apache HTTPS setup - already migrated, no changes needed
- `poodle_fix.yml`: Ansible playbook for SSL security hardening - already migrated, no changes needed
- `tests/website_https_verify.rb`: Chef InSpec tests for HTTPS functionality and SSL protocol verification - needs conversion to Ansible testing
- `tests/ssh_profile.rb`: Chef InSpec compliance profile for SSH security (STIG compliance) - needs conversion to Ansible testing
- `setup-automate/deploy-*.sh`: Chef Automate and Chef Server deployment scripts - can be removed after migration

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with ansible-lint, molecule, or native Ansible assert modules for compliance testing
- **Test Kitchen**: Replace with Molecule for infrastructure testing and verification
- **Chef Automate/Server**: Remove deployment scripts as they are no longer needed

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates generated via Ansible openssl modules - no migration needed
- SSH hardening compliance: InSpec profile tests for PermitRootLogin disabled and STIG compliance - convert to Ansible assert tasks or molecule verifiers
- POODLE vulnerability mitigation: Already implemented in Ansible (SSLProtocol -all +TLSv1.2) - no migration needed
- No hardcoded credentials detected in the reviewed files

### Technical Challenges
- **InSpec to Ansible Testing Migration**: Converting Chef InSpec compliance tests to native Ansible verification requires rewriting test logic using Ansible assert modules or uri/command modules for HTTP/SSL testing
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring the testing framework and updating CI/CD pipelines
- **Compliance Reporting**: Chef InSpec provides detailed compliance reporting - need to implement equivalent reporting with Ansible or integrate with external compliance tools

### Migration Order
1. **website_https.yml and poodle_fix.yml** (already complete - no migration needed)
2. **InSpec test conversion** (convert website_https_verify.rb and ssh_profile.rb to Ansible assert tasks)
3. **Testing framework migration** (replace Test Kitchen with Molecule for infrastructure testing)
4. **Cleanup** (remove Chef-related deployment scripts and dependencies)

### Assumptions
- The target environment will continue to use Ubuntu 20.04 LTS as specified in the current Test Kitchen configuration
- Vagrant/VirtualBox testing environment will be maintained, or the team is prepared to migrate to a different testing platform with Molecule
- The team is comfortable with losing Chef InSpec's detailed compliance reporting format in favor of Ansible's native testing capabilities
- No production Chef Automate or Chef Server infrastructure exists that depends on these example scripts
- The SSL certificate generation approach (self-signed certificates) is acceptable for the target environment, or the team will implement proper certificate management separately
- SSH security requirements will remain the same (PermitRootLogin disabled, STIG compliance) but will be verified through Ansible rather than InSpec