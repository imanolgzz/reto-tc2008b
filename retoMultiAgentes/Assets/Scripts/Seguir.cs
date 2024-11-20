using UnityEngine;

public class Seguir : MonoBehaviour
{

    public Transform target;
    public Vector3 offset = new Vector3(-10, 5, 0);
    public float followSpeed = 5f;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void LateUpdate()
    {
        if (target != null)
        {
            // Calculate the target position based on the offset
            Vector3 targetPosition = target.position + target.TransformDirection(offset);

            // Smoothly move the camera towards the target position
            transform.position = Vector3.Lerp(transform.position, targetPosition, followSpeed * Time.deltaTime);

            // Make the camera look at the target
            transform.LookAt(target);
        }
    }

}
