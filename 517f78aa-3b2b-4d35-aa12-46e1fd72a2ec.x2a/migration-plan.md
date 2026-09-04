# MIGRATION FROM CHEF INSPEC + ANSIBLE TO PURE ANSIBLE

This repository contains a hybrid Chef InSpec and Ansible demonstration setup that showcases compliance automation workflows. The migration involves consolidating the testing and configuration management into a pure Ansible solution with integrated compliance checking. The scope is limited but requires careful consideration of testing methodologies and compliance frameworks.

**Timeline Estimate**: 1-2 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (demonstration code, no production dependencies)

## Module Migration Plan

This repository contains Chef InSpec test profiles and Ansible playbooks that need consolidation into a unified Ansible approach:

### MODULE INVENTORY

**apache-https-setup**:
- Description: Apache web server configuration with SSL/TLS setup, self-signed certificate generation, and virtual host management for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible Playbook
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation, service handlers

**ssl-security-hardening**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml  
- Technology: Ansible Playbook
- Key Features: POODLE vulnerability mitigation, SSL protocol configuration, Apache SSL module hardening

**compliance-verification-https**:
- Description: InSpec compliance profile for HTTPS website verification including port listening, SSL protocol validation, and content verification
- Path: chef-and-ansible/tests/website_https_verify.rb
- Technology: Chef InSpec
- Key Features: Port 443 listening check, HTTPS response validation, SSL protocol compliance (TLS 1.2 enabled, SSL 3.0 disabled)

**ssh-security-profile**:
- Description: InSpec compliance profile for SSH security hardening verification, specifically root login restrictions
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec  
- Key Features: SSH root login disabled check, STIG compliance (RHEL-08-000227), security control validation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible provisioning with InSpec verification - needs conversion to molecule or native Ansible testing
- `chef-and-ansible/index.html`: Static HTML test content - can be retained as template or static file
- `chef-and-ansible/README.md`: Documentation explaining Chef InSpec + Ansible integration - needs updating for pure Ansible approach
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script - will be deprecated in pure Ansible environment
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script - will be deprecated in pure Ansible environment

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on kitchen.yml platform specification)
- **Virtual Machine Technology**: Vagrant (based on kitchen.yml driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with ansible-lint, molecule testing framework, and native Ansible assert modules
- **Test Kitchen**: Replace with Molecule for Ansible role testing and verification
- **Chef Automate/Server**: Remove dependency - no longer needed in pure Ansible environment
- **Vagrant**: Retain for local testing environment (compatible with Molecule)

### Security Considerations

- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - this approach can be retained and enhanced with proper certificate lifecycle management
- **SSH Security Hardening**: InSpec SSH profile checks need conversion to Ansible assert tasks or integration with ansible-hardening roles
- **Compliance Framework Integration**: STIG compliance checks (currently in InSpec) need migration to Ansible compliance roles or custom verification tasks
- **Vault/Secrets Management**: 
  - No encrypted secrets detected in current implementation
  - Hardcoded credentials found in setup scripts (userpassword='password') - these need to be moved to Ansible Vault
  - SSL certificate paths are hardcoded - should be parameterized via group_vars or host_vars

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec compliance tests to Ansible native testing requires:
  - Replacing InSpec describe blocks with Ansible assert modules
  - Implementing equivalent port, HTTP, and SSL protocol checks using Ansible modules
  - Maintaining STIG compliance validation without InSpec's built-in compliance framework
- **Compliance Reporting**: InSpec provides structured compliance reporting - need to implement equivalent reporting with Ansible facts gathering and custom reporting modules
- **Test Kitchen to Molecule**: Kitchen.yml configuration needs complete rewrite for Molecule framework including scenario definitions and verifier configuration

### Migration Order

1. **apache-https-setup** (Priority 1: Already Ansible, low risk)
   - Enhance existing playbook with better variable management
   - Add proper error handling and idempotency checks
   - Implement certificate lifecycle management

2. **ssl-security-hardening** (Priority 1: Already Ansible, security critical)
   - Integrate with apache-https-setup playbook as handlers or separate role
   - Add validation tasks to verify SSL configuration changes
   - Implement rollback procedures for failed SSL configurations

3. **compliance-verification-https** (Priority 2: Requires InSpec conversion)
   - Convert InSpec tests to Ansible assert tasks
   - Implement HTTP response validation using uri module
   - Add SSL protocol verification using openssl command module

4. **ssh-security-profile** (Priority 3: Complex compliance requirements)
   - Convert STIG compliance checks to Ansible tasks
   - Integrate with existing SSH hardening roles from Ansible Galaxy
   - Implement compliance reporting and documentation

### Assumptions

- The repository is intended for demonstration and learning purposes, not production deployment
- Ubuntu 20.04 is the target platform based on kitchen.yml, though playbooks may work on other Debian-based systems
- Self-signed certificates are acceptable for the demonstration environment (production would require proper CA-signed certificates)
- The Chef Automate/Server deployment scripts will be completely deprecated as they're not needed in a pure Ansible environment
- Test Kitchen framework knowledge exists in the team for migration to Molecule
- InSpec compliance framework knowledge exists for converting tests to Ansible native approaches
- The current hardcoded credentials in setup scripts are placeholder values for demonstration purposes
- Vagrant is the preferred local testing environment and will be retained with Molecule
- The compliance requirements (STIG controls) need to be maintained in the migrated Ansible solution
- No external Chef Supermarket cookbook dependencies exist that would complicate the migration
- The current SSL/TLS security requirements (TLS 1.2 minimum, SSL 3.0 disabled) must be preserved in the Ansible implementation