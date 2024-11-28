using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using LitJson;
using System.IO;
using Unity.VisualScripting;
using System;

public class GameManager : MonoBehaviour
{
    [SerializeField] List<GameObject> robotPrefabs;
    [SerializeField] GameObject slider, text, camera;
    Slider sliderObject;
    TextMeshProUGUI textMesh;
    public List<GameObject> robots = new List<GameObject>();
    public string jsonString;
    public JsonData jsonObject;
    public int steps, robotCount;
    float simulationSpeed = 1.0f;
    float dif = 0.5f;
    
    void Start(){
        GameObject template = GameObject.Find("IronGolem");
        robotPrefabs.Add(template); 
        string path = Path.Combine(Application.dataPath, "Data/simulation.json");
        jsonString = File.ReadAllText(path);
        jsonObject = JsonMapper.ToObject(jsonString);
        steps = jsonObject.Count;
        robotCount = jsonObject[0]["agents"].Count;
        sliderObject = slider.GetComponent<Slider>();
        textMesh = text.GetComponent<TextMeshProUGUI>();
        sliderObject.onValueChanged.AddListener(OnSliderValueChanged);
        InstantiateRobots();
    }

    void OnSliderValueChanged(float value){
        simulationSpeed = 1f + value * 20;
        textMesh.text = "Velocidad\n" + (Mathf.Round((simulationSpeed)*10)/10).ToString() + "x";
    }

    void InstantiateRobots(){
        JsonData agents = jsonObject[0]["agents"];

        for(int i = 0; i < robotCount; i++){
            float x = float.Parse(agents[i]["position"]["x"].ToString());
            float z = float.Parse(agents[i]["position"]["z"].ToString());
            int prefab = i % robotPrefabs.Count;
            float y = 0.3f;
            Vector3 position = new Vector3(x+dif, y, z+dif);   
            GameObject robot = Instantiate(robotPrefabs[prefab], position, Quaternion.identity);
            robots.Add(robot);
        }
    }

    public void StartSimulation(){
        ResetRobotPositions();
        StartCoroutine(SimulateMovement());
    }

    void MoveRobotToPoint(GameObject robot, Vector3 targetPosition){
        StartCoroutine(MoveRobot(robot, targetPosition, 1.5f/simulationSpeed - 0.1f)); // Mueve en 1 segundo
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
        for (int step = 1; step < steps; step++){
            JsonData agents = jsonObject[step]["agents"];
            JsonData racks = jsonObject[step]["racks"];
            JsonData prevAgents = jsonObject[step-1]["agents"];
            Debug.Log("Step: " + step);

            for (int i = 0; i < robotCount; i++){
                float x = float.Parse(agents[i]["position"]["x"].ToString());
                float z = float.Parse(agents[i]["position"]["z"].ToString());
                float ox = float.Parse(prevAgents[i]["position"]["x"].ToString());
                float oz = float.Parse(prevAgents[i]["position"]["z"].ToString());
                float dx = x - ox; float dz = z - oz;
                bool hasPallet = bool.Parse(agents[i]["has_pallet"].ToString());
                
                if(hasPallet){
                    robots[i].transform.Find("pallet").gameObject.SetActive(true);
                } else {
                    robots[i].transform.Find("pallet").gameObject.SetActive(false);
                }

                Vector3 targetPosition = new Vector3(x+dif, robots[i].transform.position.y, z+dif);
                if(!(dx == 0 && dz == 0)){
                    int rotation = GetRotation(dx, dz);
                    SetRotation(robots[i], rotation);
                }
                MoveRobotToPoint(robots[i], targetPosition);
            }

            for(int i = 0; i < racks.Count; i++){
                float x = float.Parse(racks[i]["position"]["x"].ToString());
                float z = float.Parse(racks[i]["position"]["z"].ToString());
                int gifts = int.Parse(racks[i]["pallets"].ToString());
                Vector3 targetPosition = new Vector3(x+dif, 2f, z+dif);
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

            yield return new WaitForSeconds(1.5f/simulationSpeed);
        }
    }

    GameObject GetObjectAt(Vector3 position, float radius = 0.1f){
        Collider[] colliders = Physics.OverlapSphere(position, radius);

        if (colliders.Length > 0){
            return colliders[0].gameObject;
        }

        return null;
    }

    public void ResetRobotPositions(){
        JsonData agents = jsonObject[0]["agents"];

        for (int i = 0; i < robots.Count; i++){
            float x = float.Parse(agents[i]["position"]["x"].ToString());
            float z = float.Parse(agents[i]["position"]["z"].ToString());

            float y = robots[i].transform.position.y; // Mantener la altura original
            Vector3 initialPosition = new Vector3(x - 0.5f, y, z - 0.5f);

            robots[i].transform.position = initialPosition;
        }
    }

    public void SetRotation(GameObject obj, int number){
        float angle = 0;

        switch (number){
            case 0:
                angle = 0f;
                break;
            case 1:
                angle = 90f;
                break;
            case 2:
                angle = 180f;
                break;
            case 3:
                angle = 270f;
                break;
            default:
                return; 
        }
        angle = angle - 180f;

        obj.transform.rotation = Quaternion.Euler(0, angle, 0);
    }

    public int GetRotation(float xChange, float zChange){
        if(xChange < 0){
            return 3;
        }

        if(xChange > 0){
            return 1;
        }

        if(zChange > 0){
            return 0;
        }
        if(zChange < 0){
            return 2;
        }

        return 0;

    }

    void FixedUpdate(){
        float cameraMoveSpeed = 20.0f * Time.deltaTime;

        Vector3 cameraPosition = camera.transform.position;

        if (Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)){
            cameraPosition.y -= cameraMoveSpeed;
            cameraPosition.z += cameraMoveSpeed;
        }

        else if (Input.GetKey(KeyCode.Space)){
            cameraPosition.y += cameraMoveSpeed;
            cameraPosition.z -= cameraMoveSpeed;
        }

        if (Input.GetKey(KeyCode.A)) {
            cameraPosition.x -= cameraMoveSpeed;
        }

        else if (Input.GetKey(KeyCode.D)){
            cameraPosition.x += cameraMoveSpeed;
        }

        if (Input.GetKey(KeyCode.W)){
            cameraPosition.z += cameraMoveSpeed;
        }

        else if (Input.GetKey(KeyCode.S)){
            cameraPosition.z -= cameraMoveSpeed;
        }

        camera.transform.position = cameraPosition;
    }
}
