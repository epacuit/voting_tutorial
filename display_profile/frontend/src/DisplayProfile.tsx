import {
  Streamlit,
  StreamlitComponentBase,
  withStreamlitConnection
} from "streamlit-component-lib";
import React, { ReactNode } from "react"
import {range} from 'underscore';
import styled from "@emotion/styled";

const Profile = styled("span")`
  margin-right:80px;
  float:left;
  width: 300px;
  overflow-x: auto;

  `
const MarginMatrix = styled("span")`
  margin-left:0px;
`

const Table = styled("table")`
  padding: 0;
  border-collapse: collapse;
  text-align: center;
  margin-bottom:20px;
  font-size:120%;
`;

const Th = styled("th")`
  font-weight:400;
  border: none !important;
  border-bottom: 2px solid #656565 !important;
  padding: 6px 13px;
`;
const Tr = styled("tr")`
  border: none !important;
  background: white !important;
`;

const Td = styled("td")`
  text-align: center;
  border: none;
  margin: 0;
  padding: 6px 13px;
`;

const TdMargin = styled("td")`
  text-align: center;
  border: 1px solid;
  margin: 0;
  padding: 6px 13px;
`;


interface State {
  numClicks: number,
  selectedCand: number,
  selectedCandMargin: number
}

/**
 * This is a React-based component template. The `render()` function is called
 * automatically when your component should be re-rendered.
 */
class DisplayProfile extends StreamlitComponentBase<State> {
  public state = { numClicks: 0, selectedCand: -1, selectedCandMargin:-1}

  private renderMarginRow = (mrow: Int32Array, ridx:number) => {
    let data:any = [];
    mrow.map((m: number, midx: number) => data.push(
    <TdMargin 
    onMouseOver={() => {this.onHoverProf(ridx); this.onHoverMatrixMargin(midx)}}
    onMouseOut={() => {this.onHoverProf(-1); this.onHoverMatrixMargin(-1)}}
    key={midx}>{m}</TdMargin>))
    return data;
  }

  public render = (): ReactNode => {
    // Arguments that are passed to the plugin in Python are accessible
    // via `this.props.args`. Here, we access the "name" arg.
    const prof = this.props.args["prof"];
    const rank_sizes = this.props.args["rank_sizes"];
    const cand_names = this.props.args["cand_names"];
    const c1 = this.props.args["c1"];
    const c2 = this.props.args["c2"];
    const margin_matrix = this.props.args["margin_matrix"];    
    const num_cands = this.props.args["num_cands"];
    const candidates = range(0, num_cands,1);
    console.log("HERE!!")
    console.log(candidates)
    console.log(cand_names)

    const css = `
    .highlight-blue {
        background-color: blue;
        color: white;
        cursor: pointer;
    }
    .highlight-red {
      background-color: red;
      color: white;
      cursor: pointer;
   }
   .highlight-gray {
    background-color: gray;
    color: white;
    cursor: pointer;
 }
`
    return (
      <span>
      <style>
        {css}
      </style>
      <Profile>
        <Table>
          <thead>
            <Tr>
              {prof.map((r: Int32Array, vidx: any) => 
                <Th>{rank_sizes[vidx]}</Th>
              )}
            </Tr>
            </thead>
            <tbody>
            {candidates.map((c,cidx) => {
              return( 
              <Tr key={cidx}> 
                {prof.map((r: Int32Array,vidx:number) => {
                  return(
                  <Td key={vidx} className = {c1 == r[cidx] ? "highlight-blue": (c2 == r[cidx]  ? "highlight-red": (this.state.selectedCand == r[cidx] ? "highlight-gray": ""))} 
                  onMouseOver={() => this.onHoverProf(r[cidx])}
                  onMouseOut={() => this.onHoverProf(-1)}>
                    {cand_names[r[cidx]]}
                    </Td>
                  )
                })}
              </Tr>)
            })}
          </tbody>
        </Table>
      </Profile>
      {margin_matrix != null ? <MarginMatrix>
        <Table>
         <tbody>
         <Tr>
            <Td></Td>
            {margin_matrix.map((row: Int32Array, ridx: number) => {
              return(<Td>{cand_names[ridx]}</Td>);
            })}
         </Tr> 
         {margin_matrix.map((mrow: Int32Array,ridx: number) => {
           console.log(mrow)
            return(<Tr key={ridx}>
              <Td>{cand_names[ridx]}</Td>
              {this.renderMarginRow(mrow, ridx)}
            </Tr>)
         })}
         </tbody>
        </Table>
      </MarginMatrix>: ""}
      </span>
    )
  }
  private onHoverProf = (c: number): void => {
    this.setState(
      prevState => ({selectedCand: c  })
    )
  }
  private onHoverMatrixMargin = (c: number): void => {
    this.setState(
      prevState => ({selectedCandMargin: c  })
    )
  }
  /** Click handler for our "Click Me!" button. */
  private onClicked = (): void => {
    // Increment state.numClicks, and pass the new value back to
    // Streamlit via `Streamlit.setComponentValue`.
    this.setState(
      prevState => ({ numClicks: prevState.numClicks + 1 }),
      () => Streamlit.setComponentValue(this.state.numClicks)
    )
  }
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
export default withStreamlitConnection(DisplayProfile)
