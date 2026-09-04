# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests integrated with Ansible playbooks for demonstration purposes. The migration scope is minimal as the repository already uses Ansible as the primary automation technology, with Chef InSpec serving as a compliance verification layer. The estimated timeline for full migration is 1-2 weeks, primarily focused on replacing InSpec tests with native Ansible compliance modules or alternative testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec compliance tests and Ansible playbooks that demonstrate integration patterns:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths have been verified using directory listing and file search tools.

- **website-https-deployment**:
    - Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: OpenSSL certificate generation, Apache virtual host configuration, SSL module activation, service management

- **poodle-vulnerability-fix**:
    - Description: SSL/TLS security hardening to disable vulnerable SSL protocols and enforce TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration remediation, protocol restriction, service restart handling

- **website-https-compliance-verification**:
    - Description: InSpec compliance tests for HTTPS service verification and SSL protocol validation
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance checks

- **ssh-security-compliance**:
    - Description: InSpec compliance profile for SSH root login security controls aligned with STIG requirements
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: STIG compliance validation, SSH configuration verification, security control mapping (SRG-OS-000112, V-38607)

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `index.html`: Static HTML test content for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for testing infrastructure
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox provider (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec (latest)**: Replace with Ansible compliance modules (ansible.posix.mount, community.general.listen_ports_facts) or Testinfra for Python-based testing
- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation
- **Vagrant**: Continue using Vagrant or migrate to container-based testing with Docker

### Security Considerations
- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates generated via OpenSSL Ansible modules - consider migrating to Let's Encrypt or internal CA integration
- **SSH Security Controls**: InSpec tests validate SSH root login restrictions - migrate to Ansible assert modules or custom validation tasks
- **Compliance Framework Integration**: Current STIG mappings in InSpec tests need translation to Ansible compliance roles or custom validation playbooks
- **Vault/secrets management**: No encrypted credentials detected in current implementation - all configurations use hardcoded values suitable for demonstration purposes

### Technical Challenges
- **InSpec Test Translation**: Converting Ruby-based InSpec controls to Ansible native testing requires rewriting test logic in YAML/Jinja2 format
- **Compliance Reporting**: InSpec provides structured compliance reporting - need to implement equivalent reporting mechanism using Ansible callback plugins or external tools
- **Test Kitchen Integration**: Current workflow relies on Test Kitchen for infrastructure provisioning and test orchestration - requires migration to Molecule or custom CI/CD pipeline

### Migration Order
1. **website-https-deployment** (already Ansible - no migration needed)
2. **poodle-vulnerability-fix** (already Ansible - no migration needed)  
3. **website-https-compliance-verification** (convert InSpec tests to Ansible assert tasks)
4. **ssh-security-compliance** (convert InSpec controls to Ansible compliance validation)

### Assumptions
- The repository serves as a demonstration/example rather than production infrastructure code
- Test Kitchen and Vagrant are acceptable for local development workflows
- InSpec compliance tests need direct translation rather than replacement with alternative compliance frameworks
- Current SSL certificate approach (self-signed) is acceptable for demonstration purposes
- No integration with external compliance management systems is required
- Ubuntu 20.04 remains the target platform (though Apache package version pinning may need updates)
- Local development and testing workflows will continue using virtualization rather than containerization