# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks. The migration involves consolidating the existing Ansible playbooks with native Ansible testing and compliance modules, eliminating the Chef InSpec dependency while maintaining the same compliance automation capabilities.

## Module Migration Plan

This repository contains hybrid Chef InSpec/Ansible examples that demonstrate compliance automation patterns:

### MODULE INVENTORY

**website-https**:
- Description: Apache HTTPS web server deployment with SSL certificate generation, virtual host configuration, and security hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, security protocol enforcement (TLS 1.2 only)

**poodle-fix**:
- Description: SSL/TLS security hardening module that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration using Vagrant driver with Ansible provisioner and InSpec verifier for integration testing
- `tests/website_https_verify.rb`: Chef InSpec compliance tests verifying HTTPS functionality, SSL protocol security, and service availability
- `tests/ssh_profile.rb`: SSH security compliance tests (referenced but not present in current tree)
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script for on-premises or cloud environments
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script with user and organization setup
- `index.html`: Static web content for demonstration purposes

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.wait_for, community.crypto.openssl_certificate_info)
- **Test Kitchen**: Migrate to Ansible Molecule for testing framework
- **Chef Automate/Server**: Remove dependency - no longer needed for pure Ansible approach

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses self-signed certificates and enforces TLS 1.2 minimum
  - Migration: Continue using community.crypto collection for certificate management
  - Enhance with proper certificate validation and rotation capabilities
- **Apache Security**: POODLE vulnerability mitigation through protocol restriction
  - Migration: Integrate security hardening into main Apache configuration playbook
- **Credential Management**: Hardcoded passwords in deployment scripts present security risk
  - Migration: Implement Ansible Vault for sensitive data management
- **Service Configuration**: Both modules manage Apache and SSH service restarts
  - Migration: Consolidate handler definitions and improve idempotency

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to native Ansible testing
  - Challenge: InSpec provides rich compliance testing DSL that needs equivalent Ansible modules
  - Mitigation: Use ansible.builtin.uri for HTTP testing, community.crypto modules for SSL validation, ansible.builtin.wait_for for port checks
- **Compliance Reporting**: Loss of Chef Automate compliance dashboard
  - Challenge: Need alternative compliance reporting mechanism
  - Mitigation: Implement custom reporting using Ansible facts and external tools like Elastic Stack or Prometheus
- **Integration Testing**: Test Kitchen provides comprehensive testing workflow
  - Challenge: Molecule learning curve and configuration differences
  - Mitigation: Gradual migration with parallel testing during transition period

### Migration Order

1. **website-https module** (moderate complexity - well-structured Ansible with clear testing requirements)
2. **poodle-fix module** (low complexity - simple configuration change that can be integrated into main Apache playbook)
3. **Testing framework migration** (high complexity - requires new tooling and test rewriting)

### Assumptions

- The repository serves as demonstration/training material rather than production infrastructure code
- Target environment will continue to use Ubuntu/Debian-based systems for Apache deployment
- Self-signed certificates are acceptable for demonstration purposes (production would require proper CA-signed certificates)
- Current Chef InSpec tests represent the minimum compliance requirements that must be maintained post-migration
- Test Kitchen workflow can be replaced with Ansible Molecule without significant process disruption
- Chef Automate server deployment scripts are for lab/demonstration environments only
- SSH configuration testing (ssh_profile.rb) exists but the actual test file is not present in the current repository
- The migration timeline assumes this is a low-priority demonstration repository rather than critical production infrastructure