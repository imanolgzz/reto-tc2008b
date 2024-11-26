using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using LitJson;
using System.IO;

public class GameManager : MonoBehaviour
{
    [SerializeField] List<GameObject> robotPrefabs;
    public List<GameObject> robots = new List<GameObject>();
    public string jsonString;
    public JsonData jsonObject;
    public int steps, robotCount;
    
    void Start(){
        string path = Path.Combine(Application.dataPath, "Data/simulation.json");
        jsonString = File.ReadAllText(path);
        jsonObject = JsonMapper.ToObject(jsonString);
        steps = jsonObject.Count;
        robotCount = jsonObject[0]["agents"].Count;
        InstantiateRobots();
    }

    void InstantiateRobots(){
        JsonData agents = jsonObject[0]["agents"];

        for(int i = 0; i < robotCount; i++){
            float x = float.Parse(agents[i]["position"]["x"].ToString());
            float z = float.Parse(agents[i]["position"]["z"].ToString());
            int prefab = i % robotPrefabs.Count;
            float y = robotPrefabs[prefab].transform.localScale.y/2;
            Vector3 position = new Vector3(x, y, z);   
            GameObject robot = Instantiate(robotPrefabs[prefab], position, Quaternion.identity);
            robots.Add(robot);
        }
    }

    public void StartSimulation(){
        StartCoroutine(SimulateMovement());
    }

    void MoveRobotToPoint(GameObject robot, Vector3 targetPosition){
        StartCoroutine(MoveRobot(robot, targetPosition, 1.4f)); // Mueve en 1 segundo
    }

   IEnumerator MoveRobot(GameObject robot, Vector3 targetPosition, float duration){
        Vector3 startPosition = robot.transform.position;
        float elapsedTime = 0f;

        while (elapsedTime < duration)
        {
            robot.transform.position = Vector3.Lerp(startPosition, targetPosition, elapsedTime / duration);
            elapsedTime += Time.deltaTime;
            yield return null; // Espera un frame
        }

        // Asegura que el robot llegue exactamente al punto de destino al final
        robot.transform.position = targetPosition;
    }

    IEnumerator SimulateMovement(){
        for (int step = 0; step < steps; step++)
        {
            JsonData agents = jsonObject[step]["agents"];
            
            for (int i = 0; i < robotCount; i++)
            {
                float x = float.Parse(agents[i]["position"]["x"].ToString());
                float z = float.Parse(agents[i]["position"]["z"].ToString());
                Vector3 targetPosition = new Vector3(x, robots[i].transform.position.y, z);
                MoveRobotToPoint(robots[i], targetPosition);
            }

            yield return new WaitForSeconds(1.5f);
        }
    }


    void Update(){
        
    }
}
