# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating integration patterns, rather than traditional Chef cookbooks requiring migration. The primary migration focus is on consolidating the compliance testing approach into native Ansible solutions while preserving the security validation capabilities.

**Migration Scope**: 2 InSpec test profiles, 2 Ansible playbooks, and Chef server deployment scripts
**Estimated Timeline**: 2-3 weeks (low complexity due to limited scope)
**Risk Level**: Low - No production cookbooks or complex dependencies

## Module Migration Plan

This repository contains Chef InSpec compliance tests integrated with Ansible playbooks that need consolidation into a unified Ansible approach:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS configuration with SSL/TLS security compliance validation using InSpec tests
- Path: chef-and-ansible/
- Technology: Ansible playbook with Chef InSpec verification
- Key Features: Self-signed certificate generation, Apache virtual host configuration, SSL protocol enforcement, compliance testing for port 443 and TLS 1.2

**ssh-security-profile**:
- Description: SSH security hardening compliance profile with STIG-based controls for root login restrictions
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG control V-38607 implementation, SSH root login validation, security audit trail requirements

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible provisioner with InSpec verifier - needs conversion to molecule testing framework
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script - can be retired as part of Chef infrastructure decommissioning
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - can be retired as part of Chef infrastructure decommissioning
- `index.html`: Static web content for demonstration - can remain as-is or be integrated into Ansible templates

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts) and external tools like Testinfra or Molecule
- **Test Kitchen**: Migrate to Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Decommission Chef infrastructure components as they are only used for demonstration purposes

### Security Considerations
- **SSL/TLS Configuration**: The existing Ansible playbook already implements proper SSL certificate generation and Apache configuration - no migration needed for core functionality
- **SSH Hardening**: Convert InSpec SSH security controls to Ansible tasks using the ansible.posix.sshd_config module for configuration management
- **Compliance Validation**: Replace InSpec compliance tests with Ansible's assert module or integrate with external compliance frameworks like OpenSCAP
- **Certificate Management**: Current implementation uses self-signed certificates - consider migrating to Let's Encrypt or proper CA-signed certificates for production use

### Technical Challenges
- **Testing Framework Migration**: Converting from Test Kitchen + InSpec to Molecule + Testinfra requires restructuring the testing approach and learning new tooling
- **Compliance Reporting**: InSpec provides detailed compliance reporting - need to implement equivalent reporting mechanisms using Ansible or external tools
- **STIG Control Mapping**: The SSH profile implements specific STIG controls that need to be preserved in the Ansible implementation with proper documentation and traceability

### Migration Order
1. **SSH Security Profile** (Priority 1): Convert InSpec SSH controls to Ansible tasks - low complexity, high security value
2. **Website HTTPS Compliance** (Priority 2): Integrate compliance validation into existing Ansible playbook using assert modules
3. **Testing Framework** (Priority 3): Migrate from Test Kitchen to Molecule for comprehensive testing automation

### Assumptions
- The repository is primarily used for demonstration and training purposes rather than production infrastructure management
- The Chef server deployment scripts can be safely retired as part of the migration to pure Ansible approach
- The existing Ansible playbooks are already well-structured and follow best practices, requiring minimal refactoring
- The target environment will continue to use Ubuntu-based systems for consistency with existing configurations
- Compliance requirements (STIG controls) must be maintained with equivalent or better validation in the Ansible implementation
- The migration team has access to Ansible testing tools like Molecule and is familiar with Ansible's built-in testing capabilities