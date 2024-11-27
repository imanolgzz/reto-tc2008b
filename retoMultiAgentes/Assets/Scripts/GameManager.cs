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

    public GameObject SelectObjectByCoordinates(float x, float y, float z){
        Vector3 targetPosition = new Vector3(x, y, z);

        foreach (GameObject robot in robots){
            if (Vector3.Distance(robot.transform.position, targetPosition) < 0.1f) {
                return robot;
            }
        }

        Debug.LogWarning("No object found at the specified coordinates!");
        return null;
    }

   IEnumerator MoveRobot(GameObject robot, Vector3 targetPosition, float duration){
        Vector3 startPosition = robot.transform.position;
        float elapsedTime = 0f;

        while (elapsedTime < duration){
            robot.transform.position = Vector3.Lerp(startPosition, targetPosition, elapsedTime / duration);
            elapsedTime += Time.deltaTime;
            yield return null; // Espera un frame
        }

        // Asegura que el robot llegue exactamente al punto de destino al final
        robot.transform.position = targetPosition;
    }

    IEnumerator SimulateMovement(){
        for (int step = 0; step < steps; step++){
            JsonData agents = jsonObject[step]["agents"];
            JsonData racks = jsonObject[step]["racks"];

            for (int i = 0; i < robotCount; i++){
                float x = float.Parse(agents[i]["position"]["x"].ToString());
                float z = float.Parse(agents[i]["position"]["z"].ToString());
                Vector3 targetPosition = new Vector3(x, robots[i].transform.position.y, z);
                MoveRobotToPoint(robots[i], targetPosition);
            }

            for(int i = 0; i < racks.Count; i++){
                float x = float.Parse(racks[i]["position"]["x"].ToString());
                float z = float.Parse(racks[i]["position"]["z"].ToString());
                int gifts = int.Parse(racks[i]["pallets"].ToString());
                Vector3 targetPosition = new Vector3(x-0.5f, 2f, z-0.5f);
                GameObject reference = GetObjectAt(targetPosition, 0.1f);
                GameObject first, second, third;
                first = reference.transform.Find("1").gameObject;    
                second = reference.transform.Find("2").gameObject;    
                third = reference.transform.Find("3").gameObject;
                if(gifts == 0){
                    first.SetActive(false);
                    second.SetActive(false);
                    third.SetActive(false);
                } else if(gifts == 1){
                    first.SetActive(true);
                    second.SetActive(false);
                    third.SetActive(false);
                } else if(gifts == 2){
                    first.SetActive(true);
                    second.SetActive(true);
                    third.SetActive(false);
                } else if(gifts == 3){
                    first.SetActive(true);
                    second.SetActive(true);
                    third.SetActive(true);
                }
            }

            yield return new WaitForSeconds(1.5f);
        }
    }

    GameObject GetObjectAt(Vector3 position, float radius = 0.1f){
        Collider[] colliders = Physics.OverlapSphere(position, radius);

        if (colliders.Length > 0){
            return colliders[0].gameObject;
        }

        return null;
    }
}
