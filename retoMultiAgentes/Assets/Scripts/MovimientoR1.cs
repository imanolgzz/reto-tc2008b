using UnityEngine;
using System.Collections.Generic;

public class RobotPathFollower : MonoBehaviour
{
    public float speed = 4.0f;          // Movement speed
    private Vector3[] pathPoints;        // Array to define waypoints for the path
    private int currentPoint = 0;       // Track the current waypoint
    private float y = 1.2025f;

    void Start()
    {

        pathPoints = new Vector3[]
        {
            new Vector3(20, y, 10),
            new Vector3(27, y, 10), 
            new Vector3(27, y, 53),
            new Vector3(90, y, 53),
            new Vector3(90, y, 77),
            new Vector3(110, y, 77),
            new Vector3(110, y, 24),
            new Vector3(20, y, 24)
        };

        transform.position = pathPoints[currentPoint];

        LookAtNextPoint();
    }

    void Update()
    {
        if (currentPoint < pathPoints.Length)
        {
            MoveTowardsWaypoint();
        }
    }

    void MoveTowardsWaypoint()
    {
        // Move towards the next point in the path
        Vector3 targetPosition = pathPoints[currentPoint];
        Vector3 direction = (targetPosition - transform.position).normalized;

        // Move in the specified direction
        transform.position += direction * speed * Time.deltaTime;

        // Check if we reached the waypoint
        if (Vector3.Distance(transform.position, targetPosition) < 0.1f)
        {
            currentPoint++;

            if (currentPoint < pathPoints.Length)
            {
                LookAtNextPoint();
            }
        }
    }

    void LookAtNextPoint()
    {
        if (currentPoint < pathPoints.Length)
        {
            // Calculate the direction to the next point
            Vector3 directionToNext = (pathPoints[currentPoint] - transform.position).normalized;

            // Adjust the direction so the object's X-axis faces the target
            Quaternion targetRotation = Quaternion.LookRotation(directionToNext, Vector3.up) * Quaternion.Euler(0, -90, 0);
            transform.rotation = targetRotation;
        }
    }
}
