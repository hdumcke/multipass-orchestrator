import sys
from multipass_orchestrator.orchestrator import MultipassOrchestrator as mpo


def main():
    if len(sys.argv) != 2:
        print("Usage %s <config.yaml>" % sys.argv[0])
        sys.exit(1)
    env = mpo(sys.argv[1])
    env.span_environment()
    env.build_environment()
    env.run_environment()


if __name__ == '__main__':
    main()
