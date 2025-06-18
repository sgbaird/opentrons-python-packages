from prefect import flow, task
import random
import time

@task
def ot2_calibration_check() -> dict:
    """Simulate OT-2 calibration check"""
    time.sleep(1)  # Simulate calibration time
    return {
        "pipette_accuracy": random.uniform(99.5, 100.0),
        "temperature": random.uniform(22.0, 24.0),
        "deck_level": "OK"
    }

@task
def process_samples(sample_count: int) -> list[str]:
    """Simulate processing laboratory samples"""
    results = []
    for i in range(sample_count):
        time.sleep(0.5)  # Simulate processing time
        success_rate = random.uniform(95.0, 100.0)
        results.append(f"Sample_{i+1}: {success_rate:.1f}% success")
    return results

@task
def generate_report(calibration: dict, samples: list[str]) -> str:
    """Generate a final report"""
    report = f"""
OT-2 Laboratory Report
=====================
Calibration Status: {calibration['deck_level']}
Pipette Accuracy: {calibration['pipette_accuracy']:.2f}%
Temperature: {calibration['temperature']:.1f}°C

Sample Results ({len(samples)} samples):
""" + "\n".join(samples)
    return report

@flow(name="OT-2 Cloud Workflow Demo")
def ot2_workflow() -> str:
    """Complete OT-2 workflow demonstrating Prefect Cloud integration"""
    
    # Run calibration check
    calibration = ot2_calibration_check()
    
    # Process samples in parallel
    sample_results = process_samples(5)
    
    # Generate final report
    report = generate_report(calibration, sample_results)
    
    print("\n" + "="*50)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("Check Prefect Cloud for full execution details!")
    print("="*50)
    
    return report

if __name__ == "__main__":
    result = ot2_workflow()
    print(result)