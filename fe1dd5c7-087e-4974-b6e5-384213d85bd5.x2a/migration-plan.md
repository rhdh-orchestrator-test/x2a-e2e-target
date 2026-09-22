# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, rather than traditional Chef cookbooks. The migration involves transitioning from a hybrid Chef InSpec + Ansible approach to a pure Ansible solution with integrated compliance testing. The scope is limited with low complexity, estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains Chef InSpec test suites and Ansible playbooks that demonstrate compliance automation patterns:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS web server deployment with SSL/TLS configuration, self-signed certificate generation, and compliance verification
- Path: chef-and-ansible/
- Technology: Ansible playbooks with Chef InSpec verification
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, POODLE vulnerability mitigation (TLS 1.2 enforcement)

**ssh-security-profile**:
- Description: SSH security compliance verification ensuring root login is disabled per security standards
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: STIG compliance checks (RHEL-08-000227), root login prevention, security audit trail requirements

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier - needs replacement with molecule or native Ansible testing
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script - can be retired as not needed for pure Ansible approach
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - can be retired as not needed for pure Ansible approach
- `index.html`: Static test content for web server verification - can be retained as test fixture

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (based on kitchen.yml platform specification and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant with VirtualBox (based on kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service, etc.) and ansible-lint for compliance
- **Test Kitchen**: Replace with Molecule for Ansible role testing and verification
- **Vagrant**: Can be retained as Molecule supports Vagrant driver, or migrate to Docker for faster testing

### Security Considerations
- **SSL/TLS Configuration**: Current playbook uses self-signed certificates - migration should implement proper certificate management with ansible-vault for production secrets
- **Hardcoded Credentials**: Deploy scripts contain plaintext passwords and usernames - must be migrated to ansible-vault encrypted variables
- **SSH Security**: InSpec SSH compliance checks need conversion to Ansible assert tasks or custom validation roles
- **POODLE Vulnerability**: SSL protocol restrictions are already implemented in Ansible - ensure continued TLS 1.2+ enforcement

### Technical Challenges
- **InSpec to Ansible Testing**: Converting Chef InSpec controls to equivalent Ansible verification tasks requires rewriting test logic using Ansible's uri, command, and assert modules
- **Test Kitchen Migration**: Replacing Test Kitchen workflow with Molecule requires restructuring test scenarios and verification approaches
- **Compliance Framework**: Loss of InSpec's built-in STIG/CIS compliance mappings - need to implement custom Ansible compliance roles or integrate with ansible-hardening collections

### Migration Order
1. **website-https-compliance** (low risk, self-contained Ansible playbook with minimal InSpec dependencies)
2. **ssh-security-profile** (moderate complexity, requires converting InSpec controls to Ansible verification tasks)
3. **Infrastructure tooling** (replace Test Kitchen with Molecule, retire Chef deployment scripts)

### Assumptions
- Target environment will remain Ubuntu-based as indicated by current playbook package management
- Self-signed certificates are acceptable for demonstration purposes - production deployment would require proper CA-signed certificates
- Vagrant-based testing approach is suitable for the target team's development workflow
- Chef Automate/Server infrastructure can be decommissioned as it's only used for demonstration purposes
- InSpec compliance reporting features are not critical requirements that need direct replacement in Ansible
- Test scenarios focus on basic web server and SSH security rather than comprehensive enterprise compliance frameworks