# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. The repository is already primarily Ansible-based with Chef InSpec used for testing and compliance verification. This represents a hybrid approach rather than a traditional Chef-to-Ansible migration scenario.

## Module Migration Plan

This repository contains demonstration examples and deployment scripts that showcase compliance automation patterns:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache web server with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for demonstration purposes
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, security hardening

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handling

**chef-infrastructure-deployment**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation and initial configuration
- Path: setup-automate/
- Technology: Bash Scripts
- Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation, system tuning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol verification, and port accessibility
- `tests/ssh_profile.rb`: InSpec security control for SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server validation
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Currently used for compliance testing and security validation. Replace with Ansible-native testing solutions:
  - **ansible-lint**: For playbook syntax and best practice validation
  - **molecule**: For infrastructure testing and validation
  - **testinfra**: For infrastructure state verification
  - **goss**: Lightweight alternative for system validation
- **Test Kitchen**: Replace with Molecule for Ansible-native testing workflows
- **Vagrant**: Can be retained or replaced with container-based testing (Docker/Podman)

### Security Considerations

- **SSL/TLS Configuration**: The examples demonstrate proper SSL hardening practices:
  - Self-signed certificate generation for development/testing
  - POODLE vulnerability mitigation (disabling SSL 3.0, enforcing TLS 1.2)
  - Proper certificate file permissions (0640)
- **SSH Hardening**: InSpec controls verify SSH root login restrictions (STIG compliance)
- **Credential Management**: 
  - Hardcoded credentials in Chef deployment scripts (userpassword='password')
  - Chef user and organization keys generated during deployment
  - No vault or encrypted credential storage currently implemented

### Technical Challenges

- **Testing Framework Migration**: Transitioning from Chef InSpec to Ansible-native testing requires:
  - Converting InSpec controls to Molecule/testinfra test cases
  - Adapting Test Kitchen workflows to Molecule scenarios
  - Maintaining compliance validation capabilities without InSpec
- **Compliance Automation**: The current hybrid approach provides strong compliance validation:
  - InSpec controls map to security frameworks (STIG, CCI)
  - Need to maintain audit trail and compliance reporting capabilities
  - Consider ansible-hardening roles for security baseline implementation
- **Chef Infrastructure Dependencies**: The deployment scripts install Chef components:
  - Evaluate if Chef Automate/Infra Server are still needed in pure Ansible environment
  - Consider migration to AWX/Ansible Tower for centralized automation

### Migration Order

1. **Testing Framework** (low risk, high value)
   - Convert InSpec tests to Molecule/testinfra
   - Establish Ansible-native CI/CD pipeline
   - Validate test coverage parity

2. **Compliance Integration** (moderate complexity)
   - Implement ansible-hardening or similar security roles
   - Establish compliance reporting without InSpec
   - Integrate with security scanning tools

3. **Infrastructure Deployment** (high complexity, dependencies)
   - Evaluate Chef infrastructure requirements
   - Migrate to AWX/Tower if centralized management needed
   - Convert bash deployment scripts to Ansible playbooks

### Assumptions

- The repository serves as demonstration/example code rather than production infrastructure
- Chef InSpec is valued for its compliance testing capabilities and security control validation
- The hybrid approach (Ansible + InSpec) may be intentional for showcasing integration patterns
- Ubuntu 20.04 target environment may need updating to more recent LTS versions
- Test Kitchen and Vagrant workflows are acceptable for development/testing environments
- Chef Automate/Infra Server deployment scripts suggest ongoing Chef infrastructure usage
- Security compliance requirements (STIG controls) must be maintained in any migration approach
- The examples focus on Apache web server configuration but patterns apply to broader infrastructure